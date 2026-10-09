"""The connector's web service: /lead for site forms, /chatwoot/webhook for chat, /health for checks."""
from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Mapping
from urllib.parse import urlparse

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response

from .brain import BrainClient
from .chatwoot import INCOMING, ChatwootClient, verify_signature
from .config import Settings
from .leads import FORMS, Lead, LeadError, contact_from_text, is_spam, parse_lead
from .prompts import (
    CRISIS_MESSAGE,
    HANDOFF_MESSAGE,
    HOLDING_MESSAGE,
    chat_system_prompt,
    guard_reply,
    is_crisis,
    load_doctrine,
    load_profile,
    summary_messages,
    wants_human,
)
from .ratelimit import SlidingWindowLimiter
from .store import Store
from .twenty import TwentyClient, TwentyError, as_list, escape_markdown

log = logging.getLogger("connector")
SUMMARY_MAX_ATTEMPTS = 200  # about three hours of one retry a minute; leads themselves are never dropped
THANKS = "Thanks. We got your request."
# A path on the site, nothing more: no scheme, no host, no "//", no query or fragment.
RETURN_PATH_RE = re.compile(r"^/(?!/)[A-Za-z0-9/_.~-]{0,200}$")


class Connector:
    """What the service does, kept apart from HTTP so it can be tested directly."""

    def __init__(
        self,
        twenty: TwentyClient,
        chatwoot: ChatwootClient,
        brain: BrainClient,
        store: Store,
        profile: str,
        doctrine: str,
    ) -> None:
        self.twenty = twenty
        self.chatwoot = chatwoot
        self.brain = brain
        self.store = store
        self.profile = profile
        self.doctrine = doctrine
        self.system_prompt = chat_system_prompt(profile)

    async def file_lead(self, lead: Lead, conversation_id: int | None = None) -> bool:
        """File the lead in Twenty and queue its summary. If Twenty is down, keep it for retry."""
        try:
            person_id, opportunity_id = await self.twenty.create_lead(lead)
        except TwentyError as exc:
            log.warning("lead kept locally, Twenty unavailable: %s", exc)
            self.store.add_pending("lead", {"lead": asdict(lead), "conversation_id": conversation_id})
            return False
        if conversation_id is not None:
            self.store.mark_lead(conversation_id)
        self.store.add_pending(
            "summary", {"lead": asdict(lead), "person_id": person_id, "opportunity_id": opportunity_id}
        )
        return True

    async def summarize(self, payload: dict[str, Any]) -> bool:
        lead = Lead(**payload["lead"])
        text = await self.brain.complete(summary_messages(lead, self.profile, self.doctrine))
        if text is None:
            return False
        lines = [escape_markdown(line.strip()) for line in text.splitlines() if line.strip()]
        await self.twenty.add_note("AI summary", as_list(lines), payload["person_id"], payload["opportunity_id"])
        return True

    async def process_pending(self) -> int:
        """Retry leads Twenty missed and summaries the model hasn't written yet. Returns how many finished."""
        finished = 0
        for item in self.store.pending():
            ok = False
            try:
                if item.kind == "lead":
                    lead = Lead(**item.payload["lead"])
                    person_id, opportunity_id = await self.twenty.create_lead(lead)
                    conversation_id = item.payload.get("conversation_id")
                    if conversation_id is not None:
                        self.store.mark_lead(conversation_id)
                    self.store.add_pending(
                        "summary", {"lead": item.payload["lead"], "person_id": person_id, "opportunity_id": opportunity_id}
                    )
                    ok = True
                elif item.kind == "summary":
                    ok = await self.summarize(item.payload)
                else:
                    ok = True
            except TwentyError as exc:
                log.warning("retry failed for %s %s: %s", item.kind, item.id, exc)
            if ok:
                self.store.remove(item.id)
                finished += 1
                continue
            self.store.bump(item.id)
            if item.kind == "summary" and item.attempts + 1 >= SUMMARY_MAX_ATTEMPTS:
                log.warning("giving up on summary %s after %s tries", item.id, item.attempts + 1)
                self.store.remove(item.id)
        return finished

    async def _say_and_hand_off(self, conversation_id: int, text: str) -> None:
        try:
            await self.chatwoot.send_message(conversation_id, text)
            await self.chatwoot.hand_off(conversation_id)
        finally:
            self.store.mark_handed_off(conversation_id)

    async def handle_chat(self, conversation_id: int, content: str, sender_name: str, status: str | None = None) -> str:
        """Answer one incoming chat message. Returns what happened: replied, holding, handoff, crisis or ignored."""
        if status == "open" or self.store.conversation(conversation_id).handed_off:
            return "ignored"
        if is_crisis(content):
            await self._say_and_hand_off(conversation_id, CRISIS_MESSAGE)
            return "crisis"
        if wants_human(content):
            await self._say_and_hand_off(conversation_id, HANDOFF_MESSAGE)
            return "handoff"

        email, phone = contact_from_text(content)
        if (email or phone) and not self.store.conversation(conversation_id).lead_created:
            lead = Lead(
                name=sender_name or "Website visitor",
                email=email,
                phone=phone,
                preferred_time="",
                message=content,
                source=FORMS["chat"],
            )
            await self.file_lead(lead, conversation_id)

        self.store.add_message(conversation_id, "user", content)
        history = self.store.history(conversation_id)
        reply = await self.brain.complete([{"role": "system", "content": self.system_prompt}, *history])
        if reply is None:
            await self._say_and_hand_off(conversation_id, HOLDING_MESSAGE)
            return "holding"
        answer = guard_reply(reply)
        await self.chatwoot.send_message(conversation_id, answer)
        self.store.add_message(conversation_id, "assistant", answer)
        return "replied"

    async def handle_chat_safely(self, conversation_id: int, content: str, sender_name: str, status: str | None) -> None:
        try:
            outcome = await self.handle_chat(conversation_id, content, sender_name, status)
            log.info("chat %s: %s", conversation_id, outcome)
        except Exception:  # noqa: BLE001 - a background task must never crash the service
            log.exception("chat %s failed", conversation_id)

    async def aclose(self) -> None:
        await self.twenty.aclose()
        await self.chatwoot.aclose()
        await self.brain.aclose()


def build_connector(settings: Settings) -> Connector:
    return Connector(
        twenty=TwentyClient(settings.twenty_url, settings.twenty_api_key),
        chatwoot=ChatwootClient(settings.chatwoot_url, settings.chatwoot_account_id, settings.chatwoot_bot_token),
        brain=BrainClient(
            settings.brain_url, settings.brain_api_key, settings.brain_model, settings.brain_timeout_s, settings.brain_max_tokens
        ),
        store=Store(Path(settings.data_dir) / "connector.db"),
        profile=load_profile(settings.graph_path),
        doctrine=load_doctrine(settings.graph_path),
    )


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _form_return_url(request: Request, form: Mapping[str, str], allowed: set[str]) -> str | None:
    """Where to send a visitor whose plain (no-JavaScript) form needs another look, or None.

    Across sites, browsers send only the origin as the referrer, so the form names its own page
    in `return_path`. Only a path on an allowed site is used, never a full address.
    """
    origin = request.headers.get("origin", "")
    if not origin:
        referer = urlparse(request.headers.get("referer", ""))
        origin = f"{referer.scheme}://{referer.netloc}" if referer.scheme and referer.netloc else ""
    if origin not in allowed:
        return None
    path = str(form.get("return_path", "") or "/")
    return f"{origin}{path if RETURN_PATH_RE.match(path) else '/'}#form-error"


def create_app(
    settings: Settings,
    connector: Connector | None = None,
    run_background: bool = True,
    clock: Callable[[], float] = time.time,
) -> FastAPI:
    service = connector or build_connector(settings)
    lead_limiter = SlidingWindowLimiter(settings.lead_limit_per_hour, 3600)
    chat_limiter = SlidingWindowLimiter(settings.chat_limit_per_minute, 60)
    allowed = set(settings.allowed_origins)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        task: asyncio.Task[None] | None = None

        async def retry_loop() -> None:
            while True:
                await asyncio.sleep(60)
                try:
                    await service.process_pending()
                except Exception:  # noqa: BLE001
                    log.exception("retry loop failed")

        if run_background:
            task = asyncio.create_task(retry_loop())
        yield
        if task:
            task.cancel()
        await service.aclose()

    app = FastAPI(title="connector", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware, allow_origins=sorted(allowed), allow_methods=["POST"], allow_headers=["Content-Type"]
    )

    def success(as_json: bool) -> Response:
        if as_json:
            return JSONResponse({"ok": True, "message": THANKS})
        return RedirectResponse(settings.thanks_url, status_code=303)

    @app.get("/health")
    async def health() -> dict[str, bool]:
        return {"ok": True}

    @app.post("/lead")
    async def lead(request: Request) -> Response:
        as_json = "application/json" in request.headers.get("content-type", "")
        try:
            raw = await request.json() if as_json else await request.form()
            form = {str(k): str(v) for k, v in dict(raw).items()}
        except Exception:  # noqa: BLE001 - any unreadable body is the visitor's problem, not a crash
            return JSONResponse({"error": "We couldn't read that form."}, status_code=400)
        if is_spam(form):
            return success(as_json)
        back = None if as_json else _form_return_url(request, form, allowed)
        if not lead_limiter.allow(f"lead:{_client_ip(request)}", clock()):
            if back:
                return RedirectResponse(back, status_code=303)
            return JSONResponse({"error": "Too many requests. Please try again later or email us."}, status_code=429)
        try:
            parsed = parse_lead(form)
        except LeadError as exc:
            if back:
                return RedirectResponse(back, status_code=303)
            return JSONResponse({"errors": exc.problems}, status_code=422)
        await service.file_lead(parsed)
        return success(as_json)

    @app.post("/chatwoot/webhook")
    async def chatwoot_webhook(request: Request, background: BackgroundTasks) -> Response:
        body = await request.body()
        if not verify_signature(
            settings.chatwoot_webhook_secret,
            request.headers.get("x-chatwoot-timestamp", ""),
            body,
            request.headers.get("x-chatwoot-signature", ""),
            clock(),
        ):
            return JSONResponse({"error": "signature check failed"}, status_code=401)
        try:
            payload = json.loads(body)
        except ValueError:
            return JSONResponse({"error": "not JSON"}, status_code=400)
        if (
            payload.get("event") != "message_created"
            or payload.get("private")
            or payload.get("message_type") not in INCOMING
        ):
            return JSONResponse({"ok": True, "action": "ignored"})
        conversation = payload.get("conversation") or {}
        conversation_id = conversation.get("id")
        content = str(payload.get("content") or "").strip()
        if not isinstance(conversation_id, int) or not content:
            return JSONResponse({"ok": True, "action": "ignored"})
        if not chat_limiter.allow(f"chat:{conversation_id}", clock()):
            return JSONResponse({"ok": True, "action": "rate_limited"})
        sender = payload.get("sender") or {}
        background.add_task(
            service.handle_chat_safely, conversation_id, content[:2000], str(sender.get("name") or ""), conversation.get("status")
        )
        return JSONResponse({"ok": True, "action": "queued"})

    return app
