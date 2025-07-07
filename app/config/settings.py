"""
Configuration settings for the TFM project.
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # LLM Configuration
    API_KEY: str = os.environ.get("API_KEY", "")
    SERVER_URL: str = os.environ.get("SERVER_URL", "")
    MODEL_ID: str = os.environ.get("MODEL_ID", "gpt-3.5-turbo")
    
    # News API Configuration
    NEWS_API_KEY: str = os.environ.get("NEWS_API_KEY", "")
    
    # Application Configuration
    DEFAULT_PAGE_SIZE: int = 10
    DEFAULT_LANGUAGE: str = "en"
    MAX_TOKENS: int = 2048
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    
    # File Paths
    DATA_DIR: str = os.path.join(os.path.dirname(__file__), '..', 'data')
    USER_INTERESTS_FILE: str = os.path.join(DATA_DIR, 'user_interests.json')
    
    # Server Configuration
    GRADIO_SERVER_NAME: str = "0.0.0.0"
    GRADIO_SERVER_PORT: int = 7860
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required environment variables are set."""
        required_vars = ["API_KEY", "SERVER_URL", "NEWS_API_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True


# Global settings instance
settings = Settings()
