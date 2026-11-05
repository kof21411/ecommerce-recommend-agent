"""配置管理 — 从环境变量/.env加载所有配置"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "development"
    SECRET_KEY: str = "dev-secret-key"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["http://localhost", "http://localhost:5173", "http://localhost:3000"]
    DATABASE_URL: str = "postgresql+asyncpg://ecomuser:ecompass@localhost:5432/ecom_agent"
    REDIS_URL: str = "redis://localhost:6379/0"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MODEL_FAST: str = "gpt-3.5-turbo"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_COLLECTION: str = "product_knowledge"
    AGENT_TEMPERATURE: float = 0.7
    AGENT_MAX_TOKENS: int = 2000
    RAG_TOP_K: int = 10
    RAG_SCORE_THRESHOLD: float = 0.6
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    PRODUCT_MANAGER_EMAILS: List[str] = []
    INDEX_TIMEOUT_SECONDS: int = 30

    class Config:
        env_file = ("../.env", ".env")
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
