"""A small client for Twenty CRM's REST API: people, opportunities and notes.

Field shapes follow Twenty's standard objects (checked against its source, v2.45):
person name {firstName, lastName}, emails {primaryEmail}, phones {primaryPhoneNumber};
opportunity stage NEW and pointOfContactId; note title and bodyV2 {markdown};
noteTargets noteId with targetPersonId / targetOpportunityId.
"""
from __future__ import annotations

import re
from typing import Any

import httpx

from .leads import Lead


class TwentyError(RuntimeError):
    """Twenty refused or could not be reached."""


def extract_id(payload: Any) -> str:
    """Twenty wraps created records, e.g. {"data": {"createPerson": {"id": ...}}}. Find the id."""
    data = payload.get("data", payload) if isinstance(payload, dict) else None
    if isinstance(data, dict):
        if isinstance(data.get("id"), str):
            return data["id"]
        for value in data.values():
            if isinstance(value, dict) and isinstance(value.get("id"), str):
                return value["id"]
    raise TwentyError(f"no record id in Twenty's response: {str(payload)[:200]}")


def person_body(lead: Lead) -> dict[str, Any]:
    body: dict[str, Any] = {"name": {"firstName": lead.first_name, "lastName": lead.last_name}}
    if lead.email:
        body["emails"] = {"primaryEmail": lead.email}
    if lead.phone:
        body["phones"] = {"primaryPhoneNumber": lead.phone}
    return body


MARKDOWN_SPECIAL_RE = re.compile(r"([\\`*_{}\[\]()<>#+!|~-])")


def escape_markdown(text: str) -> str:
    """Show visitor or model text literally in a CRM note: no links, images or formatting sneak in."""
    return MARKDOWN_SPECIAL_RE.sub(r"\\\1", text)


def fenced(text: str) -> str:
    """A code block the text can't break out of: the fence is longer than any run of backticks inside."""
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{text}\n{fence}"


def opportunity_name(lead: Lead) -> str:
    business = lead.details.get("business")
    who = f"{lead.name}, {business}" if business else lead.name
    return f"{who} ({lead.source})"


def as_list(lines: list[str]) -> str:
    """One bullet per line: plain line breaks inside a Markdown paragraph run together in the CRM."""
    return "\n".join(f"- {line}" for line in lines)


def inquiry_markdown(lead: Lead) -> str:
    lines = [f"**Source:** {lead.source}"]
    if lead.email:
        lines.append(f"**Email:** {escape_markdown(lead.email)}")
    if lead.phone:
        lines.append(f"**Phone:** {escape_markdown(lead.phone)}")
    if lead.preferred_time:
        lines.append(f"**Best time:** {escape_markdown(lead.preferred_time)}")
    lines.extend(f"**{label}:** {escape_markdown(value)}" for label, value in lead.detail_lines())
    message = fenced(lead.message) if lead.message else "_No message._"
    return f"{as_list(lines)}\n\n{message}"


class TwentyClient:
    def __init__(self, base_url: str, api_key: str, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/") + "/rest",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=20.0,
            transport=transport,
        )

    async def _create(self, path: str, body: dict[str, Any]) -> str:
        try:
            response = await self._client.post(path, json=body)
        except httpx.HTTPError as exc:
            raise TwentyError(f"could not reach Twenty: {exc}") from exc
        if response.status_code >= 400:
            raise TwentyError(f"Twenty said {response.status_code} on {path}: {response.text[:200]}")
        return extract_id(response.json())

    async def create_lead(self, lead: Lead) -> tuple[str, str]:
        """Create the person, an opportunity in the New stage, and a note with the inquiry. Returns ids."""
        person_id = await self._create("/people", person_body(lead))
        opportunity_id = await self._create(
            "/opportunities",
            {"name": opportunity_name(lead), "stage": "NEW", "pointOfContactId": person_id},
        )
        await self.add_note(f"Inquiry: {lead.source}", inquiry_markdown(lead), person_id, opportunity_id)
        return person_id, opportunity_id

    async def add_note(self, title: str, markdown: str, person_id: str, opportunity_id: str) -> str:
        note_id = await self._create("/notes", {"title": title, "bodyV2": {"markdown": markdown}})
        await self._create("/noteTargets", {"noteId": note_id, "targetOpportunityId": opportunity_id})
        await self._create("/noteTargets", {"noteId": note_id, "targetPersonId": person_id})
        return note_id

    async def aclose(self) -> None:
        await self._client.aclose()
