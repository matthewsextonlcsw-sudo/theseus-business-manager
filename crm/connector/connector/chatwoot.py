"""Chatwoot: checking that a webhook really came from Chatwoot, replying, and handing a chat to a person.

Signature scheme (from Chatwoot's lib/webhooks/trigger.rb): header X-Chatwoot-Signature is
"sha256=" + HMAC-SHA256(secret, f"{X-Chatwoot-Timestamp}.{raw body}").
"""
from __future__ import annotations

import hashlib
import hmac
from typing import Any

import httpx

INCOMING = {"incoming", 0, "0"}


class ChatwootError(RuntimeError):
    """Chatwoot refused or could not be reached."""


def sign(secret: str, timestamp: str, body: bytes) -> str:
    digest = hmac.new(secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def verify_signature(secret: str, timestamp: str, body: bytes, signature: str, now: float, tolerance_s: int = 300) -> bool:
    if not (secret and timestamp and signature):
        return False
    try:
        age = abs(now - int(timestamp))
    except ValueError:
        return False
    if age > tolerance_s:
        return False
    return hmac.compare_digest(sign(secret, timestamp, body), signature)


class ChatwootClient:
    def __init__(self, base_url: str, account_id: int, bot_token: str, transport: httpx.AsyncBaseTransport | None = None) -> None:
        # Chatwoot v4.18 takes the bot's token in the api_access_token header.
        self._client = httpx.AsyncClient(
            base_url=f"{base_url.rstrip('/')}/api/v1/accounts/{account_id}",
            headers={"api_access_token": bot_token, "Content-Type": "application/json"},
            timeout=15.0,
            transport=transport,
        )

    async def _post(self, path: str, body: dict[str, Any]) -> None:
        try:
            response = await self._client.post(path, json=body)
        except httpx.HTTPError as exc:
            raise ChatwootError(f"could not reach Chatwoot: {exc}") from exc
        if response.status_code >= 400:
            raise ChatwootError(f"Chatwoot said {response.status_code} on {path}: {response.text[:200]}")

    async def send_message(self, conversation_id: int, content: str) -> None:
        await self._post(
            f"/conversations/{conversation_id}/messages",
            {"content": content, "message_type": "outgoing", "private": False},
        )

    async def hand_off(self, conversation_id: int) -> None:
        """Opening the conversation takes it away from the bot and puts it in a person's inbox."""
        await self._post(f"/conversations/{conversation_id}/toggle_status", {"status": "open"})

    async def history(self, conversation_id: int, limit: int = 12) -> list[dict[str, str]]:
        """Recent visitor and bot messages, oldest first, as chat turns. Private notes are left out."""
        try:
            response = await self._client.get(f"/conversations/{conversation_id}/messages")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ChatwootError(f"could not read the conversation: {exc}") from exc
        turns: list[dict[str, str]] = []
        for message in response.json().get("payload", []):
            if message.get("private") or not message.get("content"):
                continue
            kind = message.get("message_type")
            if kind in INCOMING:
                turns.append({"role": "user", "content": str(message["content"])})
            elif kind in {"outgoing", 1, "1"}:
                turns.append({"role": "assistant", "content": str(message["content"])})
        return turns[-limit:]

    async def aclose(self) -> None:
        await self._client.aclose()
