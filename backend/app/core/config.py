"""
Configuration settings for PrivAI backend
"""
import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "PrivAI"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # File storage
    upload_dir: str = "uploads"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: list = [".pdf", ".csv", ".docx"]
    
    # Vector database
    faiss_index_path: str = "data/faiss_index"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # AI/LLM
    local_llm_model: str = "microsoft/DialoGPT-medium"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    
    # Database
    database_url: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Create necessary directories
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path(settings.faiss_index_path).mkdir(parents=True, exist_ok=True)
Path("data").mkdir(parents=True, exist_ok=True)
