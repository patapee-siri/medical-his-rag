"""Live augmentation: fetch credible literature on demand and cache it.

Given a query, queries the enabled providers concurrently, enforces the
credibility hard rule, de-duplicates, embeds, and upserts the new documents
into Qdrant so subsequent queries hit them locally (hybrid retrieval).
"""

from __future__ import annotations

import asyncio

from app.config import settings
from app.services.embeddings import EmbeddingService
from app.services.sources.base import FetchedDoc, LiteratureProvider, is_credible
from app.services.sources.clinicaltrials import ClinicalTrialsProvider
from app.services.sources.europepmc import EuropePMCProvider
from app.services.sources.pubmed import PubMedProvider
from app.services.vector_store import Document, VectorStore
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def _default_providers() -> list[LiteratureProvider]:
    return [PubMedProvider(), EuropePMCProvider(), ClinicalTrialsProvider()]


def _normalize_id(doc_id: str) -> str:
    return doc_id.strip().upper()


class LiveAugmentationService:
    def __init__(
        self,
        embeddings: EmbeddingService,
        vector_store: VectorStore,
        providers: list[LiteratureProvider] | None = None,
    ):
        self.embeddings = embeddings
        self.vector_store = vector_store
        self.providers = providers if providers is not None else _default_providers()

    async def augment(self, query: str, per_source_limit: int | None = None) -> int:
        """Fetch from enabled providers, filter, embed, and upsert. Returns count."""
        limit = per_source_limit or settings.LIVE_PER_SOURCE_LIMIT
        active = [p for p in self.providers if getattr(p, "enabled", True)]
        if not active:
            return 0

        results = await asyncio.gather(
            *(p.search(query, limit) for p in active),
            return_exceptions=True,
        )

        fetched: list[FetchedDoc] = []
        seen: set[str] = set()
        for res in results:
            if isinstance(res, Exception):
                logger.warning("provider_gather_error", error=str(res))
                continue
            for doc in res:
                # Hard rule: never let non-credible content through.
                if not is_credible(doc.credibility):
                    continue
                key = _normalize_id(doc.doc_id)
                if key in seen or not doc.text.strip():
                    continue
                seen.add(key)
                fetched.append(doc)

        if not fetched:
            return 0

        documents = [
            Document(
                doc_id=d.doc_id,
                title=d.title,
                text=d.text,
                source_type=d.source_type,
                url=d.url,
                authors=d.authors,
                year=d.year,
                provider=d.provider,
                credibility=d.credibility,
            )
            for d in fetched
        ]

        self.vector_store.ensure_collection(self.embeddings.dimension)
        vectors = self.embeddings.embed_documents([f"{d.title}. {d.text}" for d in documents])
        added = self.vector_store.upsert(documents, vectors)
        logger.info(
            "live_augmentation_complete",
            query=query[:80],
            providers=[p.name for p in active],
            added=added,
        )
        return added
