"""Unit tests for authentication."""
import pytest
from jose import jwt
from datetime import datetime, timedelta
from backend.app.config import config
from backend.app.api import create_access_token


class TestJWTAuthentication:
    """Test JWT token creation and validation."""
    
    def test_create_access_token(self):
        """Test JWT token creation."""
        token = create_access_token(data={"sub": "testuser"})
        assert token is not None
        assert isinstance(token, str)
    
    def test_token_contains_correct_data(self):
        """Test that token contains correct user data."""
        username = "testuser"
        token = create_access_token(data={"sub": username})
        
        # Decode token
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        assert payload["sub"] == username
        assert "exp" in payload
    
    def test_token_expiration(self):
        """Test that token has correct expiration time."""
        token = create_access_token(data={"sub": "testuser"})
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        
        exp_time = datetime.fromtimestamp(payload["exp"])
        current_time = datetime.utcnow()
        time_diff = (exp_time - current_time).total_seconds() / 60
        
        # Should be approximately equal to ACCESS_TOKEN_EXPIRE_MINUTES
        assert abs(time_diff - config.ACCESS_TOKEN_EXPIRE_MINUTES) < 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
