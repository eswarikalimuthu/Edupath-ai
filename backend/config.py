"""
EduPath AI - Application Configuration
Loaded from environment variables with safe defaults.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "EduPath AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 8501
    
    # Security & Tokens
    SECRET_KEY: str = Field(
        default="edupath-super-secret-development-key-change-in-production-32bytes",
        description="JWT signing key"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:8501,http://127.0.0.1:8501,http://localhost:8000,http://127.0.0.1:8000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        
    # Database
    DATABASE_PATH: str = str(BASE_DIR / "data" / "edupath.db")
    
    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = str(BASE_DIR / "data" / "chroma_db")
    DEFAULT_COLLECTION_NAME: str = "edupath_knowledge"
    
    # Embeddings
    EMBEDDING_PROVIDER: str = "offline_hash"  # options: offline_hash, fastembed, sentence_transformer, gemini
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    
    # RAG Settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RETRIEVAL_TOP_K: int = 5
    HYBRID_ALPHA: float = 0.6  # 0.6 dense + 0.4 BM25
    RELEVANCE_THRESHOLD: float = 0.25
    ENABLE_RERANKING: bool = True
    
    # LLM Providers
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:8b"
    
    # Upload & Security
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 120
    MAX_UPLOAD_SIZE_MB: int = 15
    ALLOWED_EXTENSIONS: str = "pdf,txt,md"
    UPLOAD_STORAGE_DIR: str = str(BASE_DIR / "data" / "uploads")

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure critical directories exist
Path(settings.DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
Path(settings.CHROMA_PERSIST_DIRECTORY).mkdir(parents=True, exist_ok=True)
Path(settings.UPLOAD_STORAGE_DIR).mkdir(parents=True, exist_ok=True)
