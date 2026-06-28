"""Application configuration loaded from environment variables.

Uses pydantic-settings so every value is validated and typed. Values are read
from a local ``.env`` file (see ``.env.example``) or the process environment.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings."""

    # --- API ---
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_KEY: str = "sk-medical-his-dev-12345"
    APP_ENV: str = "development"

    # Comma-separated list of allowed CORS origins.
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./medical_his.db"

    # --- Qdrant ---
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = "qdrant-dev-key"
    QDRANT_COLLECTION: str = "medical_documents"

    # --- HuggingFace Inference API ---
    HF_API_TOKEN: str = ""
    HF_MODEL_ID: str = "google/medgemma-1.5-7b"

    # --- Logging ---
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS origins as a clean list."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (loaded once per process)."""
    return Settings()


settings = get_settings()
