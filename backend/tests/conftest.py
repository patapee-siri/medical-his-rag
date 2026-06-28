"""Pytest fixtures: an offline TestClient with fakes for retrieval + LLM.

No Qdrant, embedding model, or network is required — the retrieval and LLM
dependencies are overridden with deterministic fakes, and the DB is a throwaway
SQLite file. This keeps the suite fast and CI-friendly.
"""

from __future__ import annotations

import pytest
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from app.db.session import Base, get_db
from app.dependencies import (
    get_consultation_service,
    get_retrieval_service,
)
from app.main import app
from app.services.consultations import ConsultationService
from app.services.llm import ChatMessage, LLMResult
from app.services.retrieval import RetrievedSource

API_KEY = "sk-medical-his-dev-12345"
AUTH = {"Authorization": f"Bearer {API_KEY}"}


# --- fakes ---------------------------------------------------------------
def sample_sources() -> list[RetrievedSource]:
    return [
        RetrievedSource(
            doc_id="PMID:1",
            title="Meningitis review",
            excerpt="Bacterial meningitis is a medical emergency…",
            text="Bacterial meningitis is a medical emergency requiring prompt therapy.",
            relevance_score=0.95,
            source_type="review",
            url="https://doi.org/10.x/abc",
            authors=["Smith J"],
            year=2020,
            provider="pubmed",
            credibility="peer_reviewed",
        )
    ]


class FakeRetrieval:
    def __init__(self, sources=None, augmented=False):
        self._sources = sources if sources is not None else sample_sources()
        self._augmented = augmented

    def retrieve(self, query, top_k=None, rerank=None):
        return self._sources

    async def retrieve_hybrid(self, query, top_k=None, rerank=None):
        return self._sources, self._augmented


class MockLLM:
    """Stands in for LLMService in mock mode."""

    model_id = "mock"
    is_configured = False

    async def generate(self, messages: list[ChatMessage]) -> LLMResult:
        return LLMResult(text="[MOCK] assessment", model="mock", is_mock=True)


class BrokenLLM:
    """Raises an unexpected error to exercise the never-500 safety net."""

    model_id = "broken-model"

    async def generate(self, messages):
        raise RuntimeError("boom")


# --- DB fixture ----------------------------------------------------------
@pytest.fixture
def db_session(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path/'test.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    yield TestingSessionLocal
    engine.dispose()


# --- client factory ------------------------------------------------------
def _make_client(db_factory, *, retrieval, llm):
    def override_get_db():
        db = db_factory()
        try:
            yield db
        finally:
            db.close()

    def override_consultation(db=Depends(get_db)):
        return ConsultationService(db=db, retrieval=retrieval, llm=llm)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_retrieval_service] = lambda: retrieval
    app.dependency_overrides[get_consultation_service] = override_consultation
    return TestClient(app)


@pytest.fixture
def client(db_session):
    """Default client: canned retrieval + mock LLM."""
    with _make_client(db_session, retrieval=FakeRetrieval(), llm=MockLLM()) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_broken_llm(db_session):
    """Client whose LLM always raises — for the never-500 regression test."""
    with _make_client(db_session, retrieval=FakeRetrieval(), llm=BrokenLLM()) as c:
        yield c
    app.dependency_overrides.clear()
