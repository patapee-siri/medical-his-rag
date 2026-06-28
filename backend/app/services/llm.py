"""LLM service backed by the HuggingFace Inference API.

Uses the OpenAI-compatible chat-completions endpoint exposed by the HF router,
so the same code works for any provider-hosted chat model. When no API token
is configured the service runs in a clearly-labelled *mock mode* so the whole
application stays runnable and demoable without external calls or cost.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.config import settings
from app.utils.exceptions import ServiceUnavailableError
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResult:
    text: str
    model: str
    is_mock: bool = False


class LLMService:
    """Async chat-completion client with a mock fallback."""

    def __init__(self, model_id: str | None = None, api_token: str | None = None):
        self.model_id = model_id or settings.HF_MODEL_ID
        self._token = api_token if api_token is not None else settings.HF_API_TOKEN
        self._base_url = settings.HF_API_BASE_URL.rstrip("/")

    @property
    def is_configured(self) -> bool:
        return bool(self._token)

    async def generate(self, messages: list[ChatMessage]) -> LLMResult:
        """Generate a chat completion, or a mock response if unconfigured."""
        if not self.is_configured:
            return self._mock(messages)

        payload = {
            "model": self.model_id,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": settings.LLM_MAX_TOKENS,
            "temperature": settings.LLM_TEMPERATURE,
        }
        headers = {"Authorization": f"Bearer {self._token}"}

        try:
            async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
                resp = await client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
            text = self._extract_text(data)
        except httpx.HTTPStatusError as exc:
            logger.error(
                "llm_http_error",
                status=exc.response.status_code,
                body=exc.response.text[:500],
                model=self.model_id,
            )
            raise ServiceUnavailableError(
                f"LLM provider returned {exc.response.status_code}"
            ) from exc
        except httpx.HTTPError as exc:
            logger.error("llm_request_failed", error=str(exc), model=self.model_id)
            raise ServiceUnavailableError("LLM provider is unreachable") from exc

        return LLMResult(text=text, model=self.model_id, is_mock=False)

    @staticmethod
    def _extract_text(data: dict) -> str:
        """Pull the assistant message out of a chat-completions payload.

        The HF router occasionally returns ``200 OK`` with an empty/malformed
        body (provider cold-start or moderation). Treat any such response as a
        provider failure so the caller degrades gracefully instead of 500-ing.
        """
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            content = None
        if not content or not str(content).strip():
            logger.error("llm_empty_response", body=str(data)[:500])
            raise ServiceUnavailableError("LLM returned an empty response")
        return str(content).strip()

    # --- mock mode ---
    def _mock(self, messages: list[ChatMessage]) -> LLMResult:
        """Return a clearly-labelled placeholder assessment (no API call)."""
        user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        complaint = ""
        for line in user.splitlines():
            if line.lower().startswith("chief complaint"):
                complaint = line.split(":", 1)[-1].strip()
                break

        text = (
            "[MOCK MODE — no HF_API_TOKEN configured; this is a placeholder]\n\n"
            "Based on the retrieved medical literature below, a clinician should "
            "correlate the presentation"
            + (f" ('{complaint}')" if complaint else "")
            + " with the cited evidence and the patient's full history. "
            "Configure HF_API_TOKEN in backend/.env to enable real model "
            "inference with MedGemma."
        )
        logger.info("llm_mock_response_used")
        return LLMResult(text=text, model="mock", is_mock=True)
