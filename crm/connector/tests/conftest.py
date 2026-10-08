"""Stand-ins for Twenty, Chatwoot and the model. No network, no real model."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import httpx
import pytest

from connector.app import Connector
from connector.brain import BrainClient
from connector.chatwoot import ChatwootClient
from connector.config import Settings
from connector.prompts import load_doctrine, load_profile
from connector.store import Store
from connector.twenty import TwentyClient

GRAPH = Path(__file__).resolve().parents[3] / "knowledge" / "business-operating.grag.json"

SETTINGS = Settings(
    twenty_url="https://crm.example",
    twenty_api_key="test-key",
    chatwoot_url="https://chat.example",
    chatwoot_account_id=1,
    chatwoot_bot_token="test-token",
    chatwoot_webhook_secret="test-secret",
    brain_url="http://brain.example/v1",
    brain_api_key="test-brain",
    brain_model="test-model",
    brain_timeout_s=5,
    brain_max_tokens=200,
    allowed_origins=("https://site.example",),
    thanks_url="https://site.example/thanks/",
    data_dir="/tmp",
    graph_path=str(GRAPH),
    lead_limit_per_hour=3,
    chat_limit_per_minute=5,
)


class FakeTwenty:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.requests: list[tuple[str, dict]] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        if self.fail:
            return httpx.Response(503, text="down")
        body = json.loads(request.content)
        self.requests.append((request.url.path, body))
        obj = request.url.path.rsplit("/", 1)[-1]
        return httpx.Response(201, json={"data": {f"create{obj}": {"id": f"{obj}-{len(self.requests)}"}}})

    def paths(self) -> list[str]:
        return [p for p, _ in self.requests]


class FakeChatwoot:
    def __init__(self, history: list[dict] | None = None) -> None:
        self.history = history or []
        self.sent: list[str] = []
        self.handoffs: list[dict] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(200, json={"payload": self.history})
        body = json.loads(request.content)
        if request.url.path.endswith("/messages"):
            self.sent.append(body["content"])
        elif request.url.path.endswith("/toggle_status"):
            self.handoffs.append(body)
        return httpx.Response(200, json={})


class FakeBrain:
    def __init__(self, reply: str = "Happy to help. What's your name and best email?", mode: str = "ok") -> None:
        self.reply = reply
        self.mode = mode
        self.calls: list[dict] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.calls.append(json.loads(request.content))
        if self.mode == "timeout":
            raise httpx.ReadTimeout("model too slow", request=request)
        if self.mode == "error":
            return httpx.Response(500, text="boom")
        return httpx.Response(200, json={"choices": [{"message": {"content": self.reply}}]})


Make = Callable[..., tuple[Connector, FakeTwenty, FakeChatwoot, FakeBrain]]


@pytest.fixture
def make_service() -> Make:
    def _make(
        twenty: FakeTwenty | None = None, chatwoot: FakeChatwoot | None = None, brain: FakeBrain | None = None
    ) -> tuple[Connector, FakeTwenty, FakeChatwoot, FakeBrain]:
        twenty = twenty or FakeTwenty()
        chatwoot = chatwoot or FakeChatwoot()
        brain = brain or FakeBrain()
        service = Connector(
            twenty=TwentyClient(SETTINGS.twenty_url, "k", transport=httpx.MockTransport(twenty.handler)),
            chatwoot=ChatwootClient(SETTINGS.chatwoot_url, 1, "t", transport=httpx.MockTransport(chatwoot.handler)),
            brain=BrainClient(SETTINGS.brain_url, "b", "m", 5, 200, transport=httpx.MockTransport(brain.handler)),
            store=Store(":memory:"),
            profile=load_profile(GRAPH),
            doctrine=load_doctrine(GRAPH),
        )
        return service, twenty, chatwoot, brain

    return _make
