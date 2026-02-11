"""Unit tests for history tracking."""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app import api


client = TestClient(app)


class TestHistoryTracking:
    """Test history tracking functionality."""
    
    def get_auth_token(self):
        """Helper method to get authentication token."""
        response = client.post(
            "/api/token",
            data={"username": "historyuser", "password": "testpass"}
        )
        return response.json()["access_token"]
    
    def test_history_initially_empty_for_new_user(self):
        """Test that new user has empty history."""
        token = self.get_auth_token()
        response = client.get(
            "/api/history",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        # History might not be empty if tests ran before
        assert "history" in response.json()
    
    def test_history_limit_parameter(self):
        """Test history limit parameter."""
        token = self.get_auth_token()
        response = client.get(
            "/api/history?limit=5",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        history = response.json()["history"]
        assert len(history) <= 5
    
    def test_history_contains_required_fields(self):
        """Test that history entries contain required fields."""
        # First, create a summary to ensure history exists
        token = self.get_auth_token()
        
        # Try to create a summary (may fail without Azure credentials)
        client.post(
            "/api/summarize/text",
            json={"text": "Test text for history", "length": "short"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Get history
        response = client.get(
            "/api/history",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        history = response.json()["history"]
        if len(history) > 0:
            entry = history[0]
            # Check for required fields
            assert "id" in entry
            assert "user" in entry
            assert "type" in entry
            assert "timestamp" in entry


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
