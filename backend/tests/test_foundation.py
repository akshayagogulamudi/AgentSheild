"""Tests for backend foundation - FEAT-001."""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app
from database import SessionLocal
from database.models import Policy, SimulatedFile, SimulatedRecord, ActivityLog


client = TestClient(app)


class TestHealthCheck:
    """Test health check endpoints."""
    
    def test_health_endpoint(self):
        """Test /health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "healthy"
    
    def test_api_status_endpoint(self):
        """Test /api/status endpoint."""
        response = client.get("/api/status")
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "operational"


class TestPolicies:
    """Test policy endpoints."""
    
    def test_get_policies(self):
        """Test GET /api/policies returns demo policies."""
        response = client.get("/api/policies")
        assert response.status_code == 200
        policies = response.json()
        assert len(policies) > 0
        assert any(p["role"] == "employee" for p in policies)
        assert any(p["role"] == "manager" for p in policies)
        assert any(p["role"] == "admin" for p in policies)
    
    def test_get_policy_by_id(self):
        """Test GET /api/policies/{id}."""
        # First get all policies
        response = client.get("/api/policies")
        policies = response.json()
        assert len(policies) > 0
        
        # Get first policy by ID
        policy_id = policies[0]["id"]
        response = client.get(f"/api/policies/{policy_id}")
        assert response.status_code == 200
        assert response.json()["id"] == policy_id
    
    def test_get_policy_not_found(self):
        """Test GET /api/policies/{id} with non-existent ID."""
        response = client.get("/api/policies/99999")
        assert response.status_code == 404


class TestDatabase:
    """Test database integrity."""
    
    def test_simulated_files_exist(self):
        """Test simulated files are seeded."""
        db = SessionLocal()
        files = db.query(SimulatedFile).all()
        db.close()
        
        assert len(files) == 5
        filenames = [f.filename for f in files]
        assert "employee_handbook.txt" in filenames
        assert "financial_records_2024.txt" in filenames
    
    def test_simulated_records_exist(self):
        """Test simulated records are seeded."""
        db = SessionLocal()
        records = db.query(SimulatedRecord).all()
        db.close()
        
        assert len(records) == 10
        record_types = set(r.record_type for r in records)
        assert "employee" in record_types
        assert "customer" in record_types
        assert "financial" in record_types
    
    def test_policies_seeded(self):
        """Test policies are seeded."""
        db = SessionLocal()
        policies = db.query(Policy).all()
        db.close()
        
        assert len(policies) == 3
        roles = [p.role for p in policies]
        assert "employee" in roles
        assert "manager" in roles
        assert "admin" in roles


class TestEvents:
    """Test events endpoints."""
    
    def test_get_events(self):
        """Test GET /api/events."""
        response = client.get("/api/events")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_activity_logs(self):
        """Test GET /api/activity-logs."""
        response = client.get("/api/activity-logs")
        assert response.status_code == 200
        logs = response.json()
        assert isinstance(logs, list)
        # Should have at least the seeding log
        assert len(logs) >= 1


class TestToolStubs:
    """Test tool stub existence."""
    
    def test_read_file_tool_exists(self):
        """Test read_file tool can be imported."""
        from tools.file_tool import read_file
        assert callable(read_file)
    
    def test_search_records_tool_exists(self):
        """Test search_records tool can be imported."""
        from tools.database_tool import search_records
        assert callable(search_records)
    
    def test_send_email_tool_exists(self):
        """Test send_email tool can be imported."""
        from tools.email_tool import send_email
        assert callable(send_email)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
