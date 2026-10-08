"""Settings, read once from the environment. A missing required value stops the service at startup."""
from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigError(RuntimeError):
    """A required setting is missing or invalid."""


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConfigError(f"missing required setting: {name}")
    return value


def _optional(name: str, default: str) -> str:
    return os.environ.get(name, "").strip() or default


def _csv(name: str) -> tuple[str, ...]:
    return tuple(v.strip() for v in os.environ.get(name, "").split(",") if v.strip())


@dataclass(frozen=True)
class Settings:
    twenty_url: str
    twenty_api_key: str
    chatwoot_url: str
    chatwoot_account_id: int
    chatwoot_bot_token: str
    chatwoot_webhook_secret: str
    brain_url: str
    brain_api_key: str
    brain_model: str
    brain_timeout_s: float
    brain_max_tokens: int
    allowed_origins: tuple[str, ...]
    thanks_url: str
    data_dir: str
    graph_path: str
    lead_limit_per_hour: int
    chat_limit_per_minute: int

    @classmethod
    def from_env(cls) -> Settings:
        try:
            account_id = int(_require("CHATWOOT_ACCOUNT_ID"))
            timeout = float(_optional("BRAIN_TIMEOUT_SECONDS", "45"))
            max_tokens = int(_optional("BRAIN_MAX_TOKENS", "1500"))
            lead_limit = int(_optional("LEAD_LIMIT_PER_HOUR", "5"))
            chat_limit = int(_optional("CHAT_LIMIT_PER_MINUTE", "6"))
        except ValueError as exc:
            raise ConfigError(f"a numeric setting is not a number: {exc}") from exc
        return cls(
            twenty_url=_require("TWENTY_URL").rstrip("/"),
            twenty_api_key=_require("TWENTY_API_KEY"),
            chatwoot_url=_require("CHATWOOT_URL").rstrip("/"),
            chatwoot_account_id=account_id,
            chatwoot_bot_token=_require("CHATWOOT_BOT_TOKEN"),
            chatwoot_webhook_secret=_require("CHATWOOT_WEBHOOK_SECRET"),
            brain_url=_require("BRAIN_URL").rstrip("/"),
            brain_api_key=_require("BRAIN_API_KEY"),
            brain_model=_require("BRAIN_MODEL"),
            brain_timeout_s=timeout,
            brain_max_tokens=max_tokens,
            allowed_origins=_csv("ALLOWED_ORIGINS"),
            thanks_url=_require("THANKS_URL"),
            data_dir=_optional("DATA_DIR", "/data"),
            graph_path=_optional("GRAPH_PATH", "/app/knowledge/business-operating.grag.json"),
            lead_limit_per_hour=lead_limit,
            chat_limit_per_minute=chat_limit,
        )
