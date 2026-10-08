"""Service tests: the /lead and /chatwoot/webhook endpoints, end to end against stand-ins."""
from __future__ import annotations

import asyncio
import json

from fastapi.testclient import TestClient

from connector.app import create_app
from connector.chatwoot import sign
from connector.prompts import CRISIS_MESSAGE, HANDOFF_MESSAGE, HOLDING_MESSAGE, PRICE_FALLBACK

from .conftest import SETTINGS, FakeBrain, FakeChatwoot, FakeTwenty, Make

NOW = 1_800_000_000.0


def client_for(service: object) -> TestClient:
    return TestClient(create_app(SETTINGS, connector=service, run_background=False, clock=lambda: NOW))


def webhook(client: TestClient, payload: dict, secret: str = "test-secret") -> object:
    body = json.dumps(payload).encode()
    ts = str(int(NOW))
    headers = {
        "Content-Type": "application/json",
        "X-Chatwoot-Timestamp": ts,
        "X-Chatwoot-Signature": sign(secret, ts, body),
    }
    return client.post("/chatwoot/webhook", content=body, headers=headers)


def incoming(content: str, conversation_id: int = 42, status: str = "pending") -> dict:
    return {
        "event": "message_created",
        "message_type": "incoming",
        "private": False,
        "content": content,
        "conversation": {"id": conversation_id, "status": status},
        "sender": {"name": "Dana Ruiz"},
    }


# /lead -------------------------------------------------------------------------------------------

def test_health(make_service: Make) -> None:
    service, *_ = make_service()
    assert client_for(service).get("/health").json() == {"ok": True}


def test_json_lead_is_filed_and_summary_queued(make_service: Make) -> None:
    service, twenty, *_ = make_service()
    response = client_for(service).post("/lead", json={"name": "Dana Ruiz", "contact": "dana@example.com", "message": "Need a site"})
    assert response.status_code == 200 and response.json()["ok"] is True
    assert twenty.paths()[:2] == ["/rest/people", "/rest/opportunities"]
    assert [p.kind for p in service.store.pending()] == ["summary"]


def test_form_lead_redirects_to_thanks(make_service: Make) -> None:
    service, *_ = make_service()
    response = client_for(service).post("/lead", data={"name": "Dana", "contact": "dana@example.com"}, follow_redirects=False)
    assert response.status_code == 303 and response.headers["location"] == SETTINGS.thanks_url


def test_honeypot_looks_successful_but_files_nothing(make_service: Make) -> None:
    service, twenty, *_ = make_service()
    response = client_for(service).post(
        "/lead", data={"name": "Bot", "contact": "bot@example.com", "website": "http://spam"}, follow_redirects=False
    )
    assert response.status_code == 303 and twenty.requests == []


def test_invalid_leads(make_service: Make) -> None:
    service, *_ = make_service()
    client = client_for(service)
    bad = client.post("/lead", json={"name": "", "contact": "nope"})
    assert bad.status_code == 422 and set(bad.json()["errors"]) == {"name", "contact"}
    back = client.post(
        "/lead", data={"name": "", "contact": "nope"},
        headers={"Referer": "https://site.example/request-consultation/"}, follow_redirects=False,
    )
    assert back.status_code == 303
    assert back.headers["location"] == "https://site.example/request-consultation/?form_error=1#form"


def test_lead_rate_limit(make_service: Make) -> None:
    service, *_ = make_service()
    client = client_for(service)
    codes = [client.post("/lead", json={"name": "A", "contact": "a@b.co"}).status_code for _ in range(4)]
    assert codes == [200, 200, 200, 429]


def test_twenty_outage_keeps_the_lead_and_retries(make_service: Make) -> None:
    twenty = FakeTwenty(fail=True)
    service, *_ = make_service(twenty=twenty)
    response = client_for(service).post("/lead", json={"name": "Dana", "contact": "dana@example.com"})
    assert response.status_code == 200
    assert [p.kind for p in service.store.pending()] == ["lead"]
    twenty.fail = False
    asyncio.run(service.process_pending())  # files the lead and queues its summary
    asyncio.run(service.process_pending())  # writes the summary note
    assert service.store.pending() == []
    assert any(body.get("title") == "AI summary" for _, body in twenty.requests)


# /chatwoot/webhook -------------------------------------------------------------------------------

def test_bad_signature_is_rejected(make_service: Make) -> None:
    service, *_ = make_service()
    assert webhook(client_for(service), incoming("hi"), secret="wrong").status_code == 401


def test_incoming_message_gets_a_model_reply(make_service: Make) -> None:
    service, _, chatwoot, brain = make_service()
    response = webhook(client_for(service), incoming("What do you do?"))
    assert response.json()["action"] == "queued"
    assert chatwoot.sent == [FakeBrain().reply]
    first = brain.calls[0]["messages"][0]
    assert first["role"] == "system" and "MWS Consulting" in first["content"]
    assert brain.calls[0]["messages"][-1] == {"role": "user", "content": "What do you do?"}


def test_model_down_sends_holding_message_and_hands_off(make_service: Make) -> None:
    service, _, chatwoot, _ = make_service(brain=FakeBrain(mode="timeout"))
    webhook(client_for(service), incoming("Do you build booking pages?"))
    assert chatwoot.sent == [HOLDING_MESSAGE]
    assert chatwoot.handoffs == [{"status": "open"}]
    assert service.store.conversation(42).handed_off


def test_crisis_skips_the_model(make_service: Make) -> None:
    service, _, chatwoot, brain = make_service()
    webhook(client_for(service), incoming("I want to end my life"))
    assert chatwoot.sent == [CRISIS_MESSAGE] and brain.calls == []


def test_asking_for_a_person_hands_off(make_service: Make) -> None:
    service, _, chatwoot, brain = make_service()
    webhook(client_for(service), incoming("Can I talk to a person?"))
    assert chatwoot.sent == [HANDOFF_MESSAGE] and chatwoot.handoffs and brain.calls == []


def test_human_owned_and_outgoing_messages_are_ignored(make_service: Make) -> None:
    service, _, chatwoot, brain = make_service()
    client = client_for(service)
    webhook(client, incoming("hello", status="open"))
    assert webhook(client, {**incoming("bot said this"), "message_type": "outgoing"}).json()["action"] == "ignored"
    assert chatwoot.sent == [] and brain.calls == []


def test_contact_in_chat_files_a_lead(make_service: Make) -> None:
    service, twenty, chatwoot, _ = make_service()
    webhook(client_for(service), incoming("Sure, I'm at dana@example.com"))
    assert twenty.paths()[0] == "/rest/people"
    assert twenty.requests[0][1]["emails"] == {"primaryEmail": "dana@example.com"}
    assert service.store.conversation(42).lead_created and len(chatwoot.sent) == 1


def test_price_in_model_reply_is_replaced(make_service: Make) -> None:
    service, _, chatwoot, _ = make_service(brain=FakeBrain(reply="That's usually $1,500."))
    webhook(client_for(service), incoming("How much is a website?"))
    assert chatwoot.sent == [PRICE_FALLBACK]
