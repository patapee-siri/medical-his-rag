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
    QDRANT_HTTPS: bool = False  # local Qdrant serves plain HTTP

    # --- Embeddings (fastembed / ONNX, no PyTorch) ---
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIM: int = 384

    # --- Retrieval ---
    RETRIEVAL_TOP_K: int = 5  # documents passed to the LLM
    RETRIEVAL_CANDIDATES: int = 20  # dense candidates fetched before re-ranking
    ENABLE_RERANKING: bool = True  # BM25 second-stage re-ranking

    # --- Live multi-source RAG (hybrid augmentation) ---
    ENABLE_LIVE_RETRIEVAL: bool = True
    LIVE_PER_SOURCE_LIMIT: int = 5  # docs fetched per provider per augmentation
    LIVE_MIN_LOCAL_HITS: int = 3  # augment if local hits fall below this
    # Augment if the best local cosine score is below this. Calibrated for
    # bge-small (high similarity floor): in-corpus ~0.71-0.80, off-corpus ~0.51-0.62.
    LIVE_SCORE_THRESHOLD: float = 0.66
    LIVE_TIMEOUT_SECONDS: int = 8  # per-provider HTTP timeout
    # Credible source toggles (preprints are intentionally absent — hard rule)
    SOURCE_PUBMED: bool = True
    SOURCE_EUROPEPMC: bool = True
    SOURCE_CLINICALTRIALS: bool = True
    NCBI_API_KEY: str = ""  # optional; raises PubMed rate limit

    # --- HuggingFace Inference API ---
    # NB: MedGemma is not served on HF's free serverless providers. Llama-3.1-8B
    # -Instruct is a reliable, widely-available default; swap via .env as needed.
    HF_API_TOKEN: str = ""
    HF_MODEL_ID: str = "meta-llama/Llama-3.1-8B-Instruct"
    HF_API_BASE_URL: str = "https://router.huggingface.co/v1"
    LLM_MAX_TOKENS: int = 512
    LLM_TEMPERATURE: float = 0.1
    LLM_TIMEOUT_SECONDS: int = 60

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
