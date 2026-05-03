"""Environment configuration using pydantic-settings.

Loads all application settings from environment variables with sensible defaults
for local development. In production, values are injected via Docker/Railway.
"""

from typing import List
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Database ──────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://lexuser:lexpass@postgres:5432/lexindia"
    # Sync URL variant for Alembic migrations (asyncpg → psycopg2)
    DATABASE_URL_SYNC: str = "postgresql://lexuser:lexpass@postgres:5432/lexindia"

    # ── Redis ─────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://redis:6379/0"

    # ── LLM Providers ─────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GROK_API_KEY: str = ""
    # Comma-separated list: "openai,gemini,grok"
    LLM_PROVIDER_ORDER: str = "openai,gemini,grok"
    INDIAN_KANOON_API_KEY: str = ""
    # Legacy alias — kept for backward compatibility with existing .env files
    KANOON_API_KEY: str = ""

    # ── Application ──────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001,https://lexindia.vercel.app"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # ── Embedding Model ──────────────────────────────────────────────────
    # all-MiniLM-L6-v2 runs locally — no API key needed.
    # Model name used by sentence-transformers for download/cache.
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # ── RAG Pipeline ─────────────────────────────────────────────────────
    SIMILARITY_THRESHOLD: float = 0.70  # Increased from 0.50 for higher confidence
    MAX_RESULTS: int = 8
    CACHE_TTL_SECONDS: int = 86400  # 24 hours
    CACHE_VERSION: str = "v3"
    MIN_RESULT_CONFIDENCE: float = 0.60  # Warn if confidence below this
    
    # ── Data Quality ───────────────────────────────────────────────
    MIN_SECTION_TEXT_LENGTH: int = 100  # Minimum characters for valid section
    MIN_SIMPLIFIED_TEXT_LENGTH: int = 50  # Minimum characters for simplified text

    @model_validator(mode="after")
    def _backfill_kanoon_key(self) -> "Settings":
        """If INDIAN_KANOON_API_KEY is empty, fall back to legacy KANOON_API_KEY."""
        if not self.INDIAN_KANOON_API_KEY and self.KANOON_API_KEY:
            self.INDIAN_KANOON_API_KEY = self.KANOON_API_KEY
        return self

    @property
    def llm_providers(self) -> List[str]:
        """Parse comma-separated LLM_PROVIDER_ORDER into a list."""
        return [p.strip().lower() for p in self.LLM_PROVIDER_ORDER.split(",")]

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse comma-separated ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"


# Singleton instance — import this throughout the app
settings = Settings()
