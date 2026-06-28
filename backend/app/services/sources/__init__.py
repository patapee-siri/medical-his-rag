"""Live literature source providers (PubMed, Europe PMC, ClinicalTrials.gov).

All providers return credibility-tagged documents. The credibility allowlist in
``base`` is the single hard rule that keeps non-peer-reviewed content (e.g.
preprints) out of the knowledge base.
"""

from app.services.sources.base import (
    CREDIBILITY_ALLOWLIST,
    FetchedDoc,
    LiteratureProvider,
    is_credible,
)

__all__ = [
    "CREDIBILITY_ALLOWLIST",
    "FetchedDoc",
    "LiteratureProvider",
    "is_credible",
]
