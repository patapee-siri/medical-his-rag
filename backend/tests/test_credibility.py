"""Tests for the credibility hard rule (no non-peer-reviewed content)."""

from app.services.live_ingest import LiveAugmentationService
from app.services.sources.base import FetchedDoc, is_credible


def test_is_credible_allowlist():
    assert is_credible("peer_reviewed") is True
    assert is_credible("clinical_registry") is True
    assert is_credible("preprint") is False
    assert is_credible(None) is False
    assert is_credible("anything_else") is False


# --- fakes for the augmentation pipeline ---
class FakeEmbeddings:
    dimension = 4

    def embed_documents(self, texts):
        return [[0.1, 0.2, 0.3, 0.4] for _ in texts]


class FakeVectorStore:
    def __init__(self):
        self.upserted = []

    def ensure_collection(self, dim):
        pass

    def upsert(self, documents, vectors):
        self.upserted.extend(documents)
        return len(documents)


class FakeProvider:
    def __init__(self, name, docs, enabled=True):
        self.name = name
        self.enabled = enabled
        self._docs = docs

    async def search(self, query, limit):
        return self._docs


def _doc(doc_id, credibility, provider="x"):
    return FetchedDoc(
        doc_id=doc_id,
        title=f"Title {doc_id}",
        text="Some abstract text about the condition.",
        provider=provider,
        credibility=credibility,
    )


async def test_augment_excludes_non_credible():
    """A preprint returned by a provider must never be indexed."""
    providers = [
        FakeProvider(
            "mixed",
            [
                _doc("PMID:1", "peer_reviewed"),
                _doc("NCT:2", "clinical_registry"),
                _doc("PPR:3", "preprint"),  # must be dropped
            ],
        )
    ]
    store = FakeVectorStore()
    svc = LiveAugmentationService(FakeEmbeddings(), store, providers=providers)

    added = await svc.augment("meningitis", per_source_limit=5)

    indexed_ids = {d.doc_id for d in store.upserted}
    assert added == 2
    assert indexed_ids == {"PMID:1", "NCT:2"}
    assert "PPR:3" not in indexed_ids


async def test_augment_dedupes_by_id():
    providers = [
        FakeProvider("a", [_doc("PMID:1", "peer_reviewed")]),
        FakeProvider("b", [_doc("pmid:1", "peer_reviewed")]),  # same id, diff case
    ]
    store = FakeVectorStore()
    svc = LiveAugmentationService(FakeEmbeddings(), store, providers=providers)

    added = await svc.augment("x")
    assert added == 1


async def test_augment_skips_disabled_providers():
    providers = [FakeProvider("off", [_doc("PMID:9", "peer_reviewed")], enabled=False)]
    store = FakeVectorStore()
    svc = LiveAugmentationService(FakeEmbeddings(), store, providers=providers)
    assert await svc.augment("x") == 0
