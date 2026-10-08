"""The model the connector asks for replies and summaries: any OpenAI-compatible chat endpoint.

Any failure (timeout, error, refusal, or an answer that was all hidden reasoning) returns None,
so the caller can fall back to a written holding message instead of guessing.
"""
from __future__ import annotations

import logging
import re

import httpx

log = logging.getLogger("connector.brain")
THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def strip_thinking(text: str) -> str:
    text = THINK_RE.sub("", text or "")
    if "</think>" in text:
        text = text.split("</think>")[-1]
    return text.strip()


class BrainClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout_s: float,
        max_tokens: int,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._model = model
        self._max_tokens = max_tokens
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=httpx.Timeout(timeout_s, connect=5.0),
            transport=transport,
        )

    async def complete(self, messages: list[dict[str, str]]) -> str | None:
        body = {"model": self._model, "messages": messages, "max_tokens": self._max_tokens, "stream": False}
        try:
            response = await self._client.post("/chat/completions", json=body)
        except httpx.HTTPError as exc:
            log.warning("model unavailable: %s", type(exc).__name__)
            return None
        if response.status_code >= 400:
            log.warning("model refused: HTTP %s", response.status_code)
            return None
        try:
            content = response.json()["choices"][0]["message"].get("content") or ""
        except (ValueError, KeyError, IndexError, TypeError):
            log.warning("model answer had an unexpected shape")
            return None
        text = strip_thinking(content)
        return text or None

    async def aclose(self) -> None:
        await self._client.aclose()
