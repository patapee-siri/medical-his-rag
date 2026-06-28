"""Unit tests for LLM response handling (the 500-fix and mock mode)."""

import pytest

from app.services.llm import ChatMessage, LLMService
from app.utils.exceptions import ServiceUnavailableError


@pytest.mark.parametrize(
    "payload",
    [
        {"choices": []},  # empty choices
        {"choices": [{"message": {"content": None}}]},  # null content
        {"choices": [{"message": {"content": "   "}}]},  # whitespace only
        {"error": "something"},  # error envelope, no choices
        {},  # empty body
    ],
)
def test_extract_text_rejects_malformed(payload):
    """A 200-OK but malformed/empty body must raise ServiceUnavailableError."""
    with pytest.raises(ServiceUnavailableError):
        LLMService._extract_text(payload)


def test_extract_text_happy():
    payload = {"choices": [{"message": {"content": "  hello  "}}]}
    assert LLMService._extract_text(payload) == "hello"


async def test_mock_mode_when_unconfigured():
    svc = LLMService(api_token="")
    assert svc.is_configured is False
    result = await svc.generate([ChatMessage(role="user", content="Chief complaint: fever")])
    assert result.is_mock is True
    assert result.model == "mock"
