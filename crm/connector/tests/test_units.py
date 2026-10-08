"""Unit tests: lead parsing, Twenty payloads, Chatwoot signatures, the model client, prompts and guards."""
from __future__ import annotations

import asyncio
import json

import httpx
import pytest

from connector.brain import BrainClient, strip_thinking
from connector.chatwoot import ChatwootClient, sign, verify_signature
from connector.leads import Lead, LeadError, contact_from_text, is_spam, parse_lead
from connector.prompts import (
    PRICE_FALLBACK,
    chat_system_prompt,
    guard_reply,
    is_crisis,
    load_profile,
    wants_human,
)
from connector.ratelimit import SlidingWindowLimiter
from connector.twenty import TwentyClient, TwentyError, extract_id

from .conftest import GRAPH, FakeTwenty


# Leads -------------------------------------------------------------------------------------------

def test_email_lead_is_cleaned_and_split() -> None:
    lead = parse_lead({"name": "  Dana   Ruiz ", "contact": "Dana@Example.com", "form": "snapshot", "message": "Hi"})
    assert (lead.first_name, lead.last_name, lead.email, lead.phone) == ("Dana", "Ruiz", "dana@example.com", "")
    assert lead.source == "Local Visibility Snapshot"


def test_phone_lead() -> None:
    lead = parse_lead({"name": "Marco", "contact": "(516) 555-0148"})
    assert lead.phone == "(516) 555-0148" and lead.email == ""


def test_bad_lead_lists_every_problem() -> None:
    with pytest.raises(LeadError) as err:
        parse_lead({"name": "", "contact": "call me maybe", "message": "x" * 2001})
    assert set(err.value.problems) == {"name", "contact", "message"}


def test_honeypot_and_contact_in_text() -> None:
    assert is_spam({"website": "http://spam.example"}) and not is_spam({"website": ""})
    assert contact_from_text("reach me at Ana@Example.com or 516-555-0101") == ("ana@example.com", "516-555-0101")


# Twenty ------------------------------------------------------------------------------------------

def test_create_lead_sends_twenty_standard_shapes() -> None:
    fake = FakeTwenty()
    client = TwentyClient("https://crm.example", "k", transport=httpx.MockTransport(fake.handler))
    lead = Lead("Dana Ruiz", "dana@example.com", "", "Mornings", "New site please", "Request consultation")
    person_id, opportunity_id = asyncio.run(client.create_lead(lead))
    assert fake.paths() == ["/rest/people", "/rest/opportunities", "/rest/notes", "/rest/noteTargets", "/rest/noteTargets"]
    bodies = [b for _, b in fake.requests]
    assert bodies[0] == {"name": {"firstName": "Dana", "lastName": "Ruiz"}, "emails": {"primaryEmail": "dana@example.com"}}
    assert bodies[1] == {"name": "Dana Ruiz (Request consultation)", "stage": "NEW", "pointOfContactId": person_id}
    assert bodies[2]["bodyV2"]["markdown"].startswith("**Source:** Request consultation")
    assert bodies[3] == {"noteId": "notes-3", "targetOpportunityId": opportunity_id}
    assert bodies[4] == {"noteId": "notes-3", "targetPersonId": person_id}


def test_extract_id_and_errors() -> None:
    assert extract_id({"data": {"createPerson": {"id": "p1"}}}) == "p1"
    assert extract_id({"id": "x"}) == "x"
    with pytest.raises(TwentyError):
        extract_id({"data": {"nothing": True}})
    down = TwentyClient("https://crm.example", "k", transport=httpx.MockTransport(FakeTwenty(fail=True).handler))
    with pytest.raises(TwentyError):
        asyncio.run(down.create_lead(Lead("A B", "a@b.co", "", "", "", "x")))


# Chatwoot ----------------------------------------------------------------------------------------

def test_signature_checks() -> None:
    body = b'{"event":"message_created"}'
    good = sign("secret", "1000", body)
    assert verify_signature("secret", "1000", body, good, now=1000)
    assert not verify_signature("other", "1000", body, good, now=1000)
    assert not verify_signature("secret", "1000", body + b" ", good, now=1000)
    assert not verify_signature("secret", "1000", body, good, now=1000 + 301)
    assert not verify_signature("secret", "", body, good, now=1000)


def test_history_keeps_visitor_and_bot_turns_only() -> None:
    payload = {"payload": [
        {"message_type": 0, "content": "hi", "private": False},
        {"message_type": 1, "content": "hello", "private": False},
        {"message_type": 1, "content": "internal note", "private": True},
        {"message_type": 2, "content": "assigned", "private": False},
    ]}
    client = ChatwootClient("https://chat.example", 1, "t", transport=httpx.MockTransport(lambda r: httpx.Response(200, json=payload)))
    assert asyncio.run(client.history(5)) == [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]


# Model client ------------------------------------------------------------------------------------

def _brain(handler: object) -> BrainClient:
    return BrainClient("http://brain.example/v1", "b", "m", 5, 100, transport=httpx.MockTransport(handler))


def test_strip_thinking() -> None:
    assert strip_thinking("<think>plan it</think>\nHello there.") == "Hello there."
    assert strip_thinking("leftover reasoning</think> Hi") == "Hi"


def test_model_failures_become_none() -> None:
    def slow(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow", request=request)

    assert asyncio.run(_brain(slow).complete([])) is None
    assert asyncio.run(_brain(lambda r: httpx.Response(500)).complete([])) is None
    empty = {"choices": [{"message": {"content": "<think>only thinking</think>"}, "finish_reason": "length"}]}
    assert asyncio.run(_brain(lambda r: httpx.Response(200, json=empty)).complete([])) is None
    ok = {"choices": [{"message": {"content": "<think>x</think>Sure."}}]}
    assert asyncio.run(_brain(lambda r: httpx.Response(200, json=ok)).complete([])) == "Sure."


# Prompts and guards ------------------------------------------------------------------------------

def test_reply_guard() -> None:
    assert guard_reply("A site like that runs about $2,500.") == PRICE_FALLBACK
    assert guard_reply("It costs 900 dollars.") == PRICE_FALLBACK
    assert guard_reply("Happy to help.") == "Happy to help."
    long = "This is a sentence. " * 80
    assert len(guard_reply(long)) <= 900 and guard_reply(long).endswith(".")


def test_crisis_and_human_detection() -> None:
    assert is_crisis("I want to end my life") and not is_crisis("my site is dying")
    assert wants_human("can I talk to a person?") and not wants_human("what do you do?")


def test_system_prompt_carries_rules_and_profile() -> None:
    profile = load_profile(GRAPH)
    prompt = chat_system_prompt(profile)
    assert "You are an AI" in prompt and "Never quote" in prompt and "988" in prompt
    assert "Floral Park" in prompt and "MWS Consulting" in prompt


def test_rate_limiter_window() -> None:
    limiter = SlidingWindowLimiter(2, 60)
    assert limiter.allow("k", 0) and limiter.allow("k", 1) and not limiter.allow("k", 2)
    assert limiter.allow("k", 61)


def test_store_round_trip() -> None:
    from connector.store import Store

    store = Store(":memory:")
    assert not store.conversation(7).handed_off
    store.mark_handed_off(7)
    store.mark_lead(7)
    assert store.conversation(7).handed_off and store.conversation(7).lead_created
    store.add_pending("summary", {"a": 1})
    item = store.pending()[0]
    store.bump(item.id)
    assert store.pending()[0].attempts == 1
    store.remove(item.id)
    assert store.pending() == []
    assert json.dumps({"ok": True})
