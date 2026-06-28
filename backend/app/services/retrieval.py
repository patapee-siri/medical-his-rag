"""Two-stage retrieval: dense vector search + optional BM25 re-ranking.

Stage 1 (dense): embed the query and fetch ``RETRIEVAL_CANDIDATES`` nearest
neighbours from Qdrant. Stage 2 (lexical): re-score those candidates with BM25
and blend the two signals, which improves precision when exact medical terms
matter. Returns the top ``RETRIEVAL_TOP_K`` sources with a normalised
relevance score in [0, 1].
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from rank_bm25 import BM25Okapi

from app.config import settings
from app.services.embeddings import EmbeddingService
from app.services.vector_store import SearchHit, VectorStore
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_DENSE_WEIGHT = 0.6
_BM25_WEIGHT = 0.4
_EXCERPT_CHARS = 320


@dataclass
class RetrievedSource:
    doc_id: str
    title: str
    excerpt: str
    text: str
    relevance_score: float
    source_type: str
    url: str | None
    authors: list[str] | None
    year: int | None


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _excerpt(text: str) -> str:
    text = text.strip()
    return text if len(text) <= _EXCERPT_CHARS else text[:_EXCERPT_CHARS].rstrip() + "…"


def _min_max_norm(values: list[float]) -> list[float]:
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi - lo < 1e-9:
        return [1.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


class RetrievalService:
    def __init__(self, embeddings: EmbeddingService, vector_store: VectorStore):
        self.embeddings = embeddings
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        rerank: bool | None = None,
    ) -> list[RetrievedSource]:
        top_k = top_k or settings.RETRIEVAL_TOP_K
        rerank = settings.ENABLE_RERANKING if rerank is None else rerank

        query_vec = self.embeddings.embed_query(query)
        candidates = self.vector_store.search(
            query_vec, limit=settings.RETRIEVAL_CANDIDATES
        )
        if not candidates:
            return []

        if rerank and len(candidates) > 1:
            ranked = self._rerank(query, candidates)
        else:
            ranked = [(hit, hit.score) for hit in candidates]

        results = [
            RetrievedSource(
                doc_id=hit.doc_id,
                title=hit.title,
                excerpt=_excerpt(hit.text),
                text=hit.text,
                relevance_score=round(score, 4),
                source_type=hit.source_type,
                url=hit.url,
                authors=hit.authors,
                year=hit.year,
            )
            for hit, score in ranked[:top_k]
        ]
        logger.info(
            "retrieval_complete",
            candidates=len(candidates),
            returned=len(results),
            reranked=rerank,
        )
        return results

    def _rerank(
        self, query: str, candidates: list[SearchHit]
    ) -> list[tuple[SearchHit, float]]:
        """Blend normalised dense and BM25 scores."""
        corpus = [_tokenize(f"{h.title} {h.text}") for h in candidates]
        bm25 = BM25Okapi(corpus)
        bm25_scores = list(bm25.get_scores(_tokenize(query)))

        dense_norm = _min_max_norm([h.score for h in candidates])
        bm25_norm = _min_max_norm(bm25_scores)

        blended = [
            (hit, _DENSE_WEIGHT * d + _BM25_WEIGHT * b)
            for hit, d, b in zip(candidates, dense_norm, bm25_norm)
        ]
        blended.sort(key=lambda pair: pair[1], reverse=True)
        return blended
