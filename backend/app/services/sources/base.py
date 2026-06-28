"""Shared types and the credibility hard-rule for live literature providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

# --- The hard rule -----------------------------------------------------------
# Only content from these credibility tiers may ever enter the knowledge base
# or be returned by retrieval. Anything else (e.g. "preprint") is dropped in
# code, not by convention. This set is the single source of truth.
CREDIBILITY_PEER_REVIEWED = "peer_reviewed"
CREDIBILITY_CLINICAL_REGISTRY = "clinical_registry"
CREDIBILITY_PREPRINT = "preprint"  # defined only so it can be explicitly excluded

CREDIBILITY_ALLOWLIST: frozenset[str] = frozenset(
    {CREDIBILITY_PEER_REVIEWED, CREDIBILITY_CLINICAL_REGISTRY}
)


def is_credible(credibility: str | None) -> bool:
    """Return True only for allowlisted (peer-reviewed / authoritative) tiers."""
    return credibility in CREDIBILITY_ALLOWLIST


@dataclass
class FetchedDoc:
    """A document fetched from a live source, ready to embed and index."""

    doc_id: str
    title: str
    text: str
    provider: str
    credibility: str
    source_type: str = "research_article"
    url: str | None = None
    authors: list[str] = field(default_factory=list)
    year: int | None = None


class LiteratureProvider(Protocol):
    """A live source that can be searched for credible literature."""

    name: str
    enabled: bool

    async def search(self, query: str, limit: int) -> list[FetchedDoc]:
        """Return up to ``limit`` documents for ``query``; never raise."""
        ...
