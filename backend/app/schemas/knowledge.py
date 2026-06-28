"""Schemas for the medical knowledge-base endpoints."""

from pydantic import BaseModel, Field


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    rerank: bool | None = None


class KnowledgeDocument(BaseModel):
    doc_id: str
    title: str
    excerpt: str
    relevance_score: float
    source_type: str
    url: str | None = None
    year: int | None = None
    provider: str = "curated"
    credibility: str = "peer_reviewed"


class KnowledgeSearchResponse(BaseModel):
    query: str
    total_returned: int
    reranked: bool
    augmented: bool = False
    documents: list[KnowledgeDocument]


class KnowledgeStatsResponse(BaseModel):
    total_documents: int
    collection: str
    embedding_model: str
    embedding_dim: int
    vector_db: str = "qdrant"
