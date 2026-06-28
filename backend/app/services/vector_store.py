"""Qdrant vector-store wrapper.

Encapsulates all Qdrant access behind a small, typed interface so the rest of
the app never touches the raw client. Handles collection creation, upserts,
and similarity search.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Stable namespace so the same doc_id always maps to the same Qdrant point id.
_ID_NAMESPACE = uuid.UUID("d3f1a9c2-0000-4000-8000-000000000001")


@dataclass
class Document:
    """A knowledge-base document to be indexed."""

    doc_id: str
    title: str
    text: str
    source_type: str = "research_article"
    url: str | None = None
    authors: list[str] | None = None
    year: int | None = None


@dataclass
class SearchHit:
    doc_id: str
    title: str
    text: str
    score: float
    source_type: str
    url: str | None
    authors: list[str] | None
    year: int | None


def _point_id(doc_id: str) -> str:
    return str(uuid.uuid5(_ID_NAMESPACE, doc_id))


class VectorStore:
    """Thin wrapper around the Qdrant client for the medical KB collection."""

    def __init__(self, client: QdrantClient | None = None, collection: str | None = None):
        self.collection = collection or settings.QDRANT_COLLECTION
        # qdrant-client auto-enables HTTPS when an api_key is set; local Qdrant
        # serves plain HTTP, so force https off for the local/dev deployment.
        self._client = client or QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            api_key=settings.QDRANT_API_KEY or None,
            https=settings.QDRANT_HTTPS,
        )

    # --- lifecycle ---
    def ensure_collection(self, dim: int) -> None:
        """Create the collection with cosine distance if it doesn't exist."""
        if self._client.collection_exists(self.collection):
            return
        logger.info("creating_qdrant_collection", collection=self.collection, dim=dim)
        self._client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

    def count(self) -> int:
        if not self._client.collection_exists(self.collection):
            return 0
        return self._client.count(self.collection).count

    def ping(self) -> bool:
        """Return True if Qdrant is reachable."""
        try:
            self._client.get_collections()
            return True
        except Exception:  # noqa: BLE001 - health probe must not raise
            return False

    # --- writes ---
    def upsert(self, documents: list[Document], vectors: list[list[float]]) -> int:
        """Upsert documents with their precomputed vectors."""
        if len(documents) != len(vectors):
            raise ValueError("documents and vectors length mismatch")

        points = [
            PointStruct(
                id=_point_id(doc.doc_id),
                vector=vector,
                payload={
                    "doc_id": doc.doc_id,
                    "title": doc.title,
                    "text": doc.text,
                    "source_type": doc.source_type,
                    "url": doc.url,
                    "authors": doc.authors or [],
                    "year": doc.year,
                },
            )
            for doc, vector in zip(documents, vectors)
        ]
        self._client.upsert(collection_name=self.collection, points=points)
        return len(points)

    # --- reads ---
    def search(self, query_vector: list[float], limit: int) -> list[SearchHit]:
        """Cosine similarity search returning the top ``limit`` hits."""
        result = self._client.query_points(
            collection_name=self.collection,
            query=query_vector,
            limit=limit,
            with_payload=True,
        )
        hits: list[SearchHit] = []
        for point in result.points:
            p = point.payload or {}
            hits.append(
                SearchHit(
                    doc_id=p.get("doc_id", str(point.id)),
                    title=p.get("title", "Untitled"),
                    text=p.get("text", ""),
                    score=float(point.score),
                    source_type=p.get("source_type", "unknown"),
                    url=p.get("url"),
                    authors=p.get("authors"),
                    year=p.get("year"),
                )
            )
        return hits
