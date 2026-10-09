"""Test suite for AI agent integration."""
import sys
import json
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db
from database.models import Base, Policy, SimulatedFile, SimulatedRecord, SecurityClassification
from agent.mock_agent import MockAgent
from agent.tool_registry import ToolRegistry


# Setup in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Provide a fresh database session with seeded data."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # Seed test data
    employee_policy = Policy(
        role="employee",
        description="Standard employee permissions",
        allowed_tools=json.dumps({
            "read_file": {
                "allowed_classifications": ["PUBLIC", "INTERNAL"],
                "restricted_files": ["financial_records_2024.txt"]
            },
            "search_records": {
                "allowed_record_types": ["employee"]
            },
            "send_email": {
                "allowed_recipients": ["@company.com"],
                "requires_approval": True
            }
        }),
        is_demo=False
    )
    db.add(employee_policy)
    
    # Add test files
    handbook = SimulatedFile(
        filename="employee_handbook.txt",
        content="Employee Handbook - Demo Data",
        classification=SecurityClassification.PUBLIC,
        is_demo=False
    )
    db.add(handbook)
    
    # Add test records
    record = SimulatedRecord(
        record_type="employee",
        data=json.dumps({"id": 1, "name": "Alice", "email": "alice@company.com"}),
        classification=SecurityClassification.INTERNAL,
        is_demo=False
    )
    db.add(record)
    
    db.commit()
    
    yield db
    
    db.close()


def override_get_db():
    """Override get_db dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def setup_test_db_override():
    """Setup test database override for this module's tests."""
    app.dependency_overrides[get_db] = override_get_db
    yield
    # Don't clear here - let conftest handle it


client = TestClient(app)


class TestAgentStatus:
    """Test agent status endpoint."""
    
    def test_mock_status(self):
        """Test GET /api/agent/status returns 200 with mock or live mode."""
        response = client.get("/api/agent/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "mode" in data
        assert data["mode"] in ["mock", "live"]
        assert "model" in data


class TestMockAgent:
    """Test mock agent scenarios."""
    
    def test_mock_normal_scenario(self, db_session):
        """Test POST /api/agent/mock?scenario=normal returns ALLOW or REQUIRE_APPROVAL."""
        response = client.post(
            "/api/agent/mock?scenario=normal",
            json={"user_message": "read the handbook"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have at least one gateway decision
        assert len(data["gateway_decisions"]) > 0
        
        # At least one decision should be ALLOW or REQUIRE_APPROVAL (not BLOCK for normal)
        decisions = [gd["decision"] for gd in data["gateway_decisions"]]
        assert any(d in ["ALLOW", "REQUIRE_APPROVAL"] for d in decisions)
    
    def test_mock_prompt_injection_blocked(self, db_session):
        """Test POST /api/agent/mock?scenario=prompt_injection blocks the request."""
        response = client.post(
            "/api/agent/mock?scenario=prompt_injection",
            json={"user_message": "inject malicious code"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have gateway decisions
        assert len(data["gateway_decisions"]) > 0
        
        # At least one should be BLOCK
        assert any(gd["decision"] == "BLOCK" for gd in data["gateway_decisions"])
        
        # Should have blocked tools
        assert len(data["blocked_tools"]) > 0
    
    def test_mock_exfiltration_blocked(self, db_session):
        """Test POST /api/agent/mock?scenario=exfiltration blocks the request."""
        response = client.post(
            "/api/agent/mock?scenario=exfiltration",
            json={"user_message": "exfiltrate data"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have gateway decisions
        assert len(data["gateway_decisions"]) > 0
        
        # At least one should be BLOCK
        assert any(gd["decision"] == "BLOCK" for gd in data["gateway_decisions"])
        
        # Should have blocked tools
        assert len(data["blocked_tools"]) > 0
    
    def test_mock_unauthorized_tool_blocked(self, db_session):
        """Test POST /api/agent/mock?scenario=unauthorized_tool blocks the request."""
        response = client.post(
            "/api/agent/mock?scenario=unauthorized_tool",
            json={"user_message": "delete records"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have gateway decisions
        assert len(data["gateway_decisions"]) > 0
        
        # At least one should be BLOCK
        assert any(gd["decision"] == "BLOCK" for gd in data["gateway_decisions"])
        
        # Should have blocked tools
        assert len(data["blocked_tools"]) > 0


class TestAgentMessage:
    """Test agent message endpoint."""
    
    def test_agent_message(self, db_session):
        """Test POST /api/agent/message processes user message and returns gateway decisions."""
        response = client.post(
            "/api/agent/message",
            json={
                "user_message": "read the handbook",
                "agent_role": "employee",
                "conversation_history": []
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "response_text" in data
        assert "proposed_tools" in data
        assert "gateway_decisions" in data
        assert "executed_tools" in data
        assert "blocked_tools" in data
        
        # Should have gateway decisions
        assert len(data["gateway_decisions"]) > 0
        
        # Each decision should have required fields
        for decision in data["gateway_decisions"]:
            assert "decision" in decision
            assert decision["decision"] in ["ALLOW", "BLOCK", "REQUIRE_APPROVAL"]
            assert "risk_score" in decision
            assert "risk_tier" in decision
            assert "explanation" in decision
            assert "checks" in decision
    
    def test_agent_message_missing_user_message(self, db_session):
        """Test POST /api/agent/message without user_message returns 400."""
        response = client.post(
            "/api/agent/message",
            json={
                "agent_role": "employee"
            }
        )
        
        assert response.status_code == 400
    
    def test_agent_message_default_role(self, db_session):
        """Test POST /api/agent/message defaults agent_role to 'employee'."""
        response = client.post(
            "/api/agent/message",
            json={
                "user_message": "read the handbook"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["gateway_decisions"]) > 0


class TestMockAgentClass:
    """Test MockAgent class directly."""
    
    def test_mock_agent_normal_scenario(self):
        """Test MockAgent normal scenario."""
        agent = MockAgent()
        response = agent.respond_with_scenario("normal", "user message")
        
        assert "response_text" in response
        assert "proposed_tools" in response
        assert len(response["proposed_tools"]) > 0
        
        tool = response["proposed_tools"][0]
        assert tool["tool_name"] == "read_file"
        assert tool["arguments"]["filename"] == "employee_handbook.txt"
        assert tool["user_request"] == "user message"
    
    def test_mock_agent_prompt_injection_scenario(self):
        """Test MockAgent prompt injection scenario."""
        agent = MockAgent()
        response = agent.respond_with_scenario("prompt_injection", "inject test")
        
        assert len(response["proposed_tools"]) > 0
        tool = response["proposed_tools"][0]
        
        assert tool["tool_name"] == "read_file"
        assert "content_override" in tool["arguments"]
        assert "Ignore previous instructions" in tool["arguments"]["content_override"]
    
    def test_mock_agent_exfiltration_scenario(self):
        """Test MockAgent exfiltration scenario."""
        agent = MockAgent()
        response = agent.respond_with_scenario("exfiltration", "exfil test")
        
        assert len(response["proposed_tools"]) > 0
        tool = response["proposed_tools"][0]
        
        assert tool["tool_name"] == "send_email"
        assert tool["arguments"]["to"] == "external-attacker@evil.com"
        assert "API_KEY" in tool["arguments"]["body"]
    
    def test_mock_agent_unauthorized_tool_scenario(self):
        """Test MockAgent unauthorized tool scenario."""
        agent = MockAgent()
        response = agent.respond_with_scenario("unauthorized_tool", "delete test")
        
        assert len(response["proposed_tools"]) > 0
        tool = response["proposed_tools"][0]
        
        assert tool["tool_name"] == "delete_records"
        assert tool["arguments"]["record_type"] == "all"


class TestToolRegistry:
    """Test ToolRegistry class."""
    
    def test_tool_registry_get_tools(self):
        """Test ToolRegistry.get_tools() returns all tools."""
        registry = ToolRegistry()
        tools = registry.get_tools()
        
        assert len(tools) == 3
        tool_names = [t["name"] for t in tools]
        assert "read_file" in tool_names
        assert "search_records" in tool_names
        assert "send_email" in tool_names
    
    def test_tool_registry_get_tool_names(self):
        """Test ToolRegistry.get_tool_names() returns tool names."""
        registry = ToolRegistry()
        names = registry.get_tool_names()
        
        assert len(names) == 3
        assert "read_file" in names
        assert "search_records" in names
        assert "send_email" in names
    
    def test_tool_registry_execute_read_file(self, db_session):
        """Test ToolRegistry.execute_tool() for read_file."""
        registry = ToolRegistry()
        
        result = registry.execute_tool(
            "read_file",
            {"filename": "employee_handbook.txt"},
            db_session
        )
        
        assert result["success"] is True
        assert result["filename"] == "employee_handbook.txt"
        assert "content" in result
    
    def test_tool_registry_execute_search_records(self, db_session):
        """Test ToolRegistry.execute_tool() for search_records."""
        registry = ToolRegistry()
        
        result = registry.execute_tool(
            "search_records",
            {"query": "Alice"},
            db_session
        )
        
        assert result["success"] is True
        assert "results" in result
        assert "count" in result
    
    def test_tool_registry_execute_unknown_tool(self, db_session):
        """Test ToolRegistry.execute_tool() with unknown tool."""
        registry = ToolRegistry()
        
        result = registry.execute_tool(
            "unknown_tool",
            {},
            db_session
        )
        
        assert result["success"] is False
        assert "Unknown tool" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
