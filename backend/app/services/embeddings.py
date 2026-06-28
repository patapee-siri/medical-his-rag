"""Embedding service backed by fastembed (ONNX runtime, no PyTorch).

The model is loaded lazily on first use; the ONNX weights (~90 MB for
bge-small) are downloaded and cached once. bge-style models distinguish
between *passage* and *query* embeddings, so we expose both.
"""

from __future__ import annotations

from functools import cached_property

from fastembed import TextEmbedding

from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Wraps a fastembed model to produce document and query vectors."""

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL

    @cached_property
    def _model(self) -> TextEmbedding:
        logger.info("loading_embedding_model", model=self.model_name)
        return TextEmbedding(model_name=self.model_name)

    @property
    def dimension(self) -> int:
        return settings.EMBEDDING_DIM

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of passages for indexing."""
        if not texts:
            return []
        return [vec.tolist() for vec in self._model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query (uses the model's query representation)."""
        vec = next(self._model.query_embed(text))
        return vec.tolist()

    def warm_up(self) -> None:
        """Force model load (used on startup so the first request is fast)."""
        _ = self._model
