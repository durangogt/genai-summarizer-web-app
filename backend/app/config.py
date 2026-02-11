"""Application configuration management."""
import os
from typing import Literal
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""
    
    # GitHub Models Configuration
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_MODELS_ENDPOINT: str = os.getenv("GITHUB_MODELS_ENDPOINT", "https://models.inference.ai.azure.com")
    GITHUB_MODEL_NAME: str = os.getenv("GITHUB_MODEL_NAME", "gpt-4o")
    
    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    MAX_BATCH_FILES: int = int(os.getenv("MAX_BATCH_FILES", "10"))
    ALLOWED_EXTENSIONS: set = {".txt", ".pdf", ".docx", ".html"}
    
    # Summary Configuration
    SUMMARY_LENGTHS = {
        "short": {"max_tokens": 150, "description": "Brief summary (1-2 sentences)"},
        "medium": {"max_tokens": 300, "description": "Balanced summary (2-4 sentences)"},
        "long": {"max_tokens": 600, "description": "Detailed summary (4-8 sentences)"}
    }
    DEFAULT_SUMMARY_LENGTH: Literal["short", "medium", "long"] = "medium"
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "app.log")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        if not cls.GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        if not cls.GITHUB_MODELS_ENDPOINT:
            raise ValueError("GITHUB_MODELS_ENDPOINT environment variable is required")
        return True


# Global config instance
config = Config()
