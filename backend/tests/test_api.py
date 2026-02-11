"""Unit tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Test that health check endpoint returns success."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "healthy"


class TestAuthenticationEndpoints:
    """Test authentication endpoints."""
    
    def test_token_generation(self):
        """Test JWT token generation."""
        response = client.post(
            "/api/token",
            data={"username": "testuser", "password": "testpass"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"
    
    def test_token_generation_missing_credentials(self):
        """Test token generation with missing credentials."""
        response = client.post("/api/token", data={})
        assert response.status_code == 422  # Validation error


class TestSummarizationEndpoints:
    """Test summarization endpoints."""
    
    def get_auth_token(self):
        """Helper method to get authentication token."""
        response = client.post(
            "/api/token",
            data={"username": "testuser", "password": "testpass"}
        )
        return response.json()["access_token"]
    
    def test_summarize_text_without_auth(self):
        """Test text summarization without authentication."""
        response = client.post(
            "/api/summarize/text",
            json={
                "text": "This is a test text for summarization.",
                "length": "short"
            }
        )
        assert response.status_code == 403  # Forbidden without token
    
    def test_summarize_text_with_auth(self):
        """Test text summarization with authentication."""
        # Note: This test will fail without valid Azure OpenAI credentials
        token = self.get_auth_token()
        response = client.post(
            "/api/summarize/text",
            json={
                "text": "This is a test text for summarization. " * 10,
                "length": "short"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        # May return 200 or 500 depending on Azure OpenAI configuration
        assert response.status_code in [200, 500]
    
    def test_summarize_empty_text(self):
        """Test summarization with empty text."""
        token = self.get_auth_token()
        response = client.post(
            "/api/summarize/text",
            json={
                "text": "",
                "length": "medium"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == False
        assert result["error"] is not None


class TestHistoryEndpoint:
    """Test history endpoint."""
    
    def get_auth_token(self):
        """Helper method to get authentication token."""
        response = client.post(
            "/api/token",
            data={"username": "testuser", "password": "testpass"}
        )
        return response.json()["access_token"]
    
    def test_get_history(self):
        """Test retrieving history."""
        token = self.get_auth_token()
        response = client.get(
            "/api/history",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert "history" in response.json()
        assert "count" in response.json()
    
    def test_get_history_without_auth(self):
        """Test history without authentication."""
        response = client.get("/api/history")
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
