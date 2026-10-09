"""Integration tests for complete AgentShield workflows."""
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
from database.models import Base, Policy, SecurityEvent, Threat
from models import ToolCallRequest


# Setup in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

# Enable foreign keys for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables once at module load
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Provide a fresh database session with seeded data."""
    # Clear all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # Seed test data
    employee_policy = Policy(
        role="employee",
        description="Standard employee permissions",
        allowed_tools=json.dumps({
            "read_file": {
                "restricted_files": ["financial_records_2024.txt", "salary_data.txt"],
                "allowed_classifications": ["PUBLIC", "INTERNAL"]
            },
            "search_records": {
                "allowed_classifications": ["PUBLIC"]
            },
            "send_email": False
        }),
        is_demo=False
    )
    
    manager_policy = Policy(
        role="manager",
        description="Manager permissions",
        allowed_tools=json.dumps({
            "read_file": {
                "restricted_files": [],
                "allowed_classifications": ["PUBLIC", "INTERNAL", "RESTRICTED"]
            },
            "search_records": {
                "allowed_classifications": ["PUBLIC", "INTERNAL"]
            },
            "send_email": {"requires_approval": True}
        }),
        is_demo=False
    )
    
    db.add(employee_policy)
    db.add(manager_policy)
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


class TestFullAttackPipeline:
    """Test complete attack detection and blocking pipeline."""
    
    def test_full_attack_pipeline_injection(self, db_session):
        """
        Test full attack pipeline for prompt injection scenario.
        
        POST /api/agent/mock?scenario=prompt_injection should:
        - Block the tool call
        - Return response with blocked_tools containing at least one tool
        - Return response with gateway_decisions containing at least one BLOCK decision
        """
        response = client.post("/api/agent/mock?scenario=prompt_injection")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "blocked_tools" in data
        assert "gateway_decisions" in data
        
        # Verify at least one tool is blocked
        assert len(data["blocked_tools"]) > 0, "Expected at least one tool to be blocked"
        
        # Verify at least one BLOCK decision
        block_decisions = [d for d in data["gateway_decisions"] if d.get("decision") == "BLOCK"]
        assert len(block_decisions) > 0, "Expected at least one BLOCK decision in gateway_decisions"
    
    def test_full_attack_pipeline_exfiltration(self, db_session):
        """
        Test full attack pipeline for data exfiltration scenario.
        
        POST /api/agent/mock?scenario=exfiltration should:
        - Block the tool call
        - Return response with blocked_tools containing at least one tool
        - Return response with gateway_decisions containing at least one BLOCK decision
        """
        response = client.post("/api/agent/mock?scenario=exfiltration")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "blocked_tools" in data
        assert "gateway_decisions" in data
        
        # Verify at least one tool is blocked
        assert len(data["blocked_tools"]) > 0, "Expected at least one tool to be blocked for exfiltration"
        
        # Verify at least one BLOCK decision
        block_decisions = [d for d in data["gateway_decisions"] if d.get("decision") == "BLOCK"]
        assert len(block_decisions) > 0, "Expected at least one BLOCK decision for exfiltration scenario"
    
    def test_full_attack_pipeline_unauthorized(self, db_session):
        """
        Test full attack pipeline for unauthorized tool scenario.
        
        POST /api/agent/mock?scenario=unauthorized_tool should:
        - Block the tool call
        - Return response with blocked_tools containing at least one tool
        - Return response with gateway_decisions containing at least one BLOCK decision
        """
        response = client.post("/api/agent/mock?scenario=unauthorized_tool")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "blocked_tools" in data
        assert "gateway_decisions" in data
        
        # Verify at least one tool is blocked
        assert len(data["blocked_tools"]) > 0, "Expected at least one tool to be blocked for unauthorized_tool"
        
        # Verify at least one BLOCK decision
        block_decisions = [d for d in data["gateway_decisions"] if d.get("decision") == "BLOCK"]
        assert len(block_decisions) > 0, "Expected at least one BLOCK decision for unauthorized_tool scenario"


class TestEventsRecording:
    """Test that events are properly recorded after gateway evaluation."""
    
    def test_events_recorded_after_gateway(self, db_session):
        """
        Test that security events are recorded after gateway evaluation.
        
        POST /api/gateway/evaluate with a tool call, then GET /api/events should
        return at least one event with the evaluated tool.
        """
        # Evaluate a tool through the gateway
        request_data = {
            "tool_name": "read_file",
            "arguments": {"filename": "employee_handbook.txt"},
            "user_request": "Read the employee handbook",
            "agent_name": "test_agent",
            "agent_role": "employee"
        }
        
        response = client.post("/api/gateway/evaluate", json=request_data)
        assert response.status_code == 200
        
        # Fetch events
        response = client.get("/api/events")
        assert response.status_code == 200
        
        events = response.json()
        assert isinstance(events, list)
        assert len(events) > 0, "Expected at least one security event to be recorded"
        
        # Verify the event has the evaluated tool
        event = events[0]
        assert event["requested_tool"] == "read_file"
        assert "decision" in event
        assert "risk_score" in event


class TestApprovalWorkflow:
    """Test approval workflow for restricted operations."""
    
    def test_approval_created_for_email(self, db_session):
        """
        Test that approval is required for email from manager.
        
        POST /api/gateway/evaluate with tool=send_email, agent_role=manager
        should return decision REQUIRE_APPROVAL or BLOCK.
        """
        request_data = {
            "tool_name": "send_email",
            "arguments": {
                "to": "recipient@company.com",
                "subject": "Test",
                "body": "Test message"
            },
            "user_request": "Send an email",
            "agent_name": "test_agent",
            "agent_role": "manager"
        }
        
        response = client.post("/api/gateway/evaluate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should require approval or be blocked
        assert data["decision"] in ["REQUIRE_APPROVAL", "BLOCK"], \
            f"Expected REQUIRE_APPROVAL or BLOCK, got {data['decision']}"


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_endpoint(self, db_session):
        """
        Test GET /health returns 200.
        """
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_gateway_health_endpoint(self, db_session):
        """
        Test GET /api/gateway/health returns 200.
        """
        response = client.get("/api/gateway/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "operational"


class TestNormalScenario:
    """Test normal, legitimate usage scenarios."""
    
    def test_normal_scenario_allows_safe_tool(self, db_session):
        """
        Test that normal scenario with safe tool returns ALLOW decision.
        """
        response = client.post("/api/agent/mock?scenario=normal")
        
        assert response.status_code == 200
        data = response.json()
        
        # Normal scenario should have allow or executed tools
        assert len(data.get("proposed_tools", [])) > 0
        
        # At least one tool should be proposed
        gateway_decisions = data.get("gateway_decisions", [])
        assert len(gateway_decisions) > 0
        
        # Should not all be blocked
        allow_decisions = [d for d in gateway_decisions if d.get("decision") == "ALLOW"]
        block_decisions = [d for d in gateway_decisions if d.get("decision") == "BLOCK"]
        
        # At least one should be allowed or approved
        assert len(allow_decisions) > 0 or len(data.get("executed_tools", [])) > 0, \
            "Expected at least one tool to be allowed in normal scenario"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
