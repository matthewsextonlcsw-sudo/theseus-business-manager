"""Turning a submitted form into a clean lead, or a list of problems."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Mapping

EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,253}\.[A-Za-z]{2,24}$")
PHONE_DIGITS_RE = re.compile(r"\d")
EMAIL_IN_TEXT_RE = re.compile(r"[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,253}\.[A-Za-z]{2,24}")
PHONE_IN_TEXT_RE = re.compile(r"(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")

FORMS = {"consultation": "Request consultation", "snapshot": "Local Visibility Snapshot", "chat": "Website chat"}
HONEYPOT_FIELD = "website"
LIMITS = {"name": 120, "email": 200, "phone": 40, "contact": 200, "preferred_time": 120, "message": 2000}
# Optional intake questions a site form may ask, as field name: (label in the CRM, length limit).
# Anything else a form sends is ignored, never stored. The site address is `site_url` because
# `website` is the spam trap.
DETAIL_FIELDS = {
    "role": ("Role", 120),
    "business": ("Business", 160),
    "city": ("City or service area", 120),
    "site_url": ("Website", 300),
    "profile_url": ("Google Business Profile", 300),
    "work_type": ("Work type", 80),
    "deadline": ("Deadline or dependency", 300),
}
NO_CONTACT = "Please give an email address or a phone number we can reach you at."


class LeadError(ValueError):
    """The form can't become a lead. `problems` maps field names to plain-language reasons."""

    def __init__(self, problems: dict[str, str]) -> None:
        super().__init__("; ".join(f"{k}: {v}" for k, v in problems.items()))
        self.problems = problems


@dataclass(frozen=True)
class Lead:
    name: str
    email: str
    phone: str
    preferred_time: str
    message: str
    source: str
    details: dict[str, str] = field(default_factory=dict)

    @property
    def first_name(self) -> str:
        return self.name.split(" ", 1)[0]

    @property
    def last_name(self) -> str:
        parts = self.name.split(" ", 1)
        return parts[1] if len(parts) > 1 else ""

    @property
    def contact(self) -> str:
        return self.email or self.phone

    def detail_lines(self) -> list[tuple[str, str]]:
        """The optional answers with their labels, in a fixed order."""
        return [(label, self.details[key]) for key, (label, _) in DETAIL_FIELDS.items() if self.details.get(key)]


def is_spam(form: Mapping[str, str]) -> bool:
    """A person never fills the hidden field; bots usually do."""
    return bool(str(form.get(HONEYPOT_FIELD, "")).strip())


def _clean(value: object) -> str:
    return " ".join(str(value or "").split())


def _is_phone(value: str) -> bool:
    return len(PHONE_DIGITS_RE.findall(value)) >= 10


def _contact(form: Mapping[str, str], values: dict[str, str], problems: dict[str, str]) -> tuple[str, str]:
    """Read separate email and phone fields, or the single `contact` field older forms send."""
    if "email" not in form and "phone" not in form:
        contact = values["contact"]
        if EMAIL_RE.match(contact):
            return contact.lower(), ""
        if _is_phone(contact):
            return "", contact
        problems.setdefault("contact", NO_CONTACT)
        return "", ""

    email = phone = ""
    if values["email"]:
        if EMAIL_RE.match(values["email"]):
            email = values["email"].lower()
        else:
            problems.setdefault("email", "Please check the email address.")
    if values["phone"]:
        if _is_phone(values["phone"]):
            phone = values["phone"]
        else:
            problems.setdefault("phone", "Please include the area code.")
    if not values["email"] and not values["phone"]:
        problems.setdefault("email", NO_CONTACT)
    return email, phone


def parse_lead(form: Mapping[str, str]) -> Lead:
    values = {key: _clean(form.get(key, "")) for key in LIMITS}
    message = str(form.get("message", "") or "").strip()
    values["message"] = message
    source = FORMS.get(_clean(form.get("form", "")), FORMS["consultation"])

    problems: dict[str, str] = {}
    if not values["name"]:
        problems["name"] = "Please tell us your name."
    for key, limit in LIMITS.items():
        if len(values[key]) > limit:
            problems[key] = f"Please keep this under {limit} characters."

    details: dict[str, str] = {}
    for key, (_label, limit) in DETAIL_FIELDS.items():
        value = _clean(form.get(key, ""))
        if len(value) > limit:
            problems[key] = f"Please keep this under {limit} characters."
        elif value:
            details[key] = value

    email, phone = _contact(form, values, problems)
    if problems:
        raise LeadError(problems)
    return Lead(
        name=values["name"],
        email=email,
        phone=phone,
        preferred_time=values["preferred_time"],
        message=message,
        source=source,
        details=details,
    )


def contact_from_text(text: str) -> tuple[str, str]:
    """Find an email address or US phone number a visitor typed into a chat."""
    email = EMAIL_IN_TEXT_RE.search(text or "")
    phone = PHONE_IN_TEXT_RE.search(text or "")
    return (email.group(0).lower() if email else "", phone.group(0) if phone else "")
