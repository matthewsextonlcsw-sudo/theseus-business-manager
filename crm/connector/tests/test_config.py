"""Settings must fail loudly at startup when something required is missing or malformed."""
from __future__ import annotations

import pytest

from connector.app import Connector, build_connector
from connector.config import ConfigError, Settings

from .conftest import GRAPH

REQUIRED = {
    "TWENTY_URL": "https://crm.example/",
    "TWENTY_API_KEY": "k",
    "CHATWOOT_URL": "https://chat.example",
    "CHATWOOT_ACCOUNT_ID": "1",
    "CHATWOOT_BOT_TOKEN": "t",
    "CHATWOOT_WEBHOOK_SECRET": "s",
    "BRAIN_URL": "http://brain.example/v1/",
    "BRAIN_API_KEY": "b",
    "BRAIN_MODEL": "m",
    "THANKS_URL": "https://site.example/thanks/",
}


def _env(monkeypatch: pytest.MonkeyPatch, **overrides: str) -> None:
    for key, value in {**REQUIRED, **overrides}.items():
        monkeypatch.setenv(key, value)


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    _env(monkeypatch, ALLOWED_ORIGINS="https://a.example, https://b.example")
    settings = Settings.from_env()
    assert settings.twenty_url == "https://crm.example"
    assert settings.brain_url == "http://brain.example/v1"
    assert settings.allowed_origins == ("https://a.example", "https://b.example")
    assert (settings.brain_timeout_s, settings.lead_limit_per_hour) == (45.0, 5)


def test_missing_setting_stops_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    _env(monkeypatch)
    monkeypatch.delenv("BRAIN_API_KEY")
    with pytest.raises(ConfigError, match="BRAIN_API_KEY"):
        Settings.from_env()


def test_bad_number_stops_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    _env(monkeypatch, CHATWOOT_ACCOUNT_ID="one")
    with pytest.raises(ConfigError, match="not a number"):
        Settings.from_env()


def test_build_connector_wires_everything(monkeypatch: pytest.MonkeyPatch, tmp_path: object) -> None:
    _env(monkeypatch, DATA_DIR=str(tmp_path), GRAPH_PATH=str(GRAPH))
    service = build_connector(Settings.from_env())
    assert isinstance(service, Connector)
    assert "MWS Consulting" in service.system_prompt
