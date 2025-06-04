"""
Configuration settings for Spartacus Backend
"""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Use ConfigDict for Pydantic v2
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow"  # Allow extra fields from .env
    )
    
    # Server configuration
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Auto-reload on code changes")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins"
    )
    
    # Agent configuration
    max_agents: int = Field(default=10, description="Maximum number of concurrent agents")
    agent_timeout: int = Field(default=300, description="Agent timeout in seconds")
    
    # Chat configuration
    max_chat_history: int = Field(default=100, description="Maximum chat history length")
    enable_streaming: bool = Field(default=True, description="Enable WebSocket streaming")
    
    # LLM configuration
    default_model: str = Field(default="gpt-4", description="Default LLM model")
    max_tokens: int = Field(default=4000, description="Maximum tokens per request")
    temperature: float = Field(default=0.7, description="LLM temperature")
    
    # Azure OpenAI configuration
    azure_openai_endpoint: str = Field(default="", description="Azure OpenAI endpoint")
    azure_openai_model: str = Field(default="gpt-4", description="Azure OpenAI model")
    azure_openai_api_version: str = Field(default="2024-10-21", description="Azure OpenAI API version")
    azure_openai_api_key: str = Field(default="", description="Azure OpenAI API key")
    
    # Additional Azure OpenAI endpoints
    azure_openai_endpoint_us_gpt4o_mini: str = Field(default="", description="Azure OpenAI US endpoint for GPT-4o mini")
    azure_openai_api_version_us_gpt4o_mini: str = Field(default="2023-03-15-preview", description="Azure OpenAI US API version for GPT-4o mini")
    azure_openai_model_us_gpt4o_mini: str = Field(default="gpt-4o-mini", description="Azure OpenAI US model for GPT-4o mini")
    azure_openai_key_us_gpt4o_mini: str = Field(default="", description="Azure OpenAI US API key for GPT-4o mini")
    
    # OpenAI configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    
    # Other service tokens
    hf_access_token_summarizer: str = Field(default="", description="HuggingFace access token for summarizer")
    logfire_token: str = Field(default="", description="Logfire token")
    
    # Paths
    data_dir: str = Field(default="./data", description="Data directory")
    logs_dir: str = Field(default="./logs", description="Logs directory")


def get_settings() -> Settings:
    """Get settings instance with lazy initialization"""
    return Settings()


# For backwards compatibility, create a default instance
# but move it to a function to avoid import-time execution issues
def get_default_settings() -> Settings:
    """Get default settings instance"""
    settings = get_settings()
    
    # Ensure directories exist
    os.makedirs(settings.data_dir, exist_ok=True)
    os.makedirs(settings.logs_dir, exist_ok=True)
    
    return settings


# Global settings instance for backwards compatibility
settings = get_default_settings() 