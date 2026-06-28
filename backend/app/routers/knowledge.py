"""Medical knowledge-base endpoints (semantic search + stats)."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.config import settings
from app.dependencies import (
    RequireAuth,
    get_retrieval_service,
    get_vector_store,
)
from app.schemas.knowledge import (
    KnowledgeDocument,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    KnowledgeStatsResponse,
)
from app.services.retrieval import RetrievalService
from app.services.vector_store import VectorStore

router = APIRouter(
    prefix="/knowledge",
    tags=["knowledge"],
    dependencies=[RequireAuth],
)


@router.post(
    "/search",
    response_model=KnowledgeSearchResponse,
    summary="Semantic search over the medical knowledge base",
)
def search_knowledge(
    payload: KnowledgeSearchRequest,
    retrieval: Annotated[RetrievalService, Depends(get_retrieval_service)],
) -> KnowledgeSearchResponse:
    reranked = settings.ENABLE_RERANKING if payload.rerank is None else payload.rerank
    sources = retrieval.retrieve(
        payload.query, top_k=payload.top_k, rerank=payload.rerank
    )
    return KnowledgeSearchResponse(
        query=payload.query,
        total_returned=len(sources),
        reranked=reranked,
        documents=[
            KnowledgeDocument(
                doc_id=s.doc_id,
                title=s.title,
                excerpt=s.excerpt,
                relevance_score=s.relevance_score,
                source_type=s.source_type,
                url=s.url,
                year=s.year,
            )
            for s in sources
        ],
    )


@router.get(
    "/stats",
    response_model=KnowledgeStatsResponse,
    summary="Knowledge-base statistics",
)
def knowledge_stats(
    store: Annotated[VectorStore, Depends(get_vector_store)],
) -> KnowledgeStatsResponse:
    return KnowledgeStatsResponse(
        total_documents=store.count(),
        collection=settings.QDRANT_COLLECTION,
        embedding_model=settings.EMBEDDING_MODEL,
        embedding_dim=settings.EMBEDDING_DIM,
    )
