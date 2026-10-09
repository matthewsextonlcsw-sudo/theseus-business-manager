"""Local state in SQLite: each chat's recent turns, which chats have a lead or were handed off, and work
waiting to be retried.

Nothing a visitor sends is lost if Twenty or the model is down: it waits here and is retried.
Chatwoot lets a bot post messages but not read a conversation, so the turns the model needs are kept
here: the last CHAT_KEEP_MESSAGES of each chat, for CHAT_KEEP_DAYS.
"""
from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CHAT_KEEP_MESSAGES = 40
CHAT_KEEP_DAYS = 30

SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
  conversation_id INTEGER PRIMARY KEY,
  lead_created INTEGER NOT NULL DEFAULT 0,
  handed_off INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS pending (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL,
  payload TEXT NOT NULL,
  attempts INTEGER NOT NULL DEFAULT 0,
  created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id INTEGER NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS messages_by_chat ON messages (conversation_id, id);
CREATE INDEX IF NOT EXISTS messages_by_age ON messages (created_at);
"""


@dataclass(frozen=True)
class Conversation:
    conversation_id: int
    lead_created: bool
    handed_off: bool


@dataclass(frozen=True)
class PendingItem:
    id: int
    kind: str
    payload: dict[str, Any]
    attempts: int


class Store:
    def __init__(self, path: str | Path) -> None:
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(path), check_same_thread=False)
        self._db.executescript(SCHEMA)
        self._db.commit()

    def conversation(self, conversation_id: int) -> Conversation:
        row = self._db.execute(
            "SELECT lead_created, handed_off FROM conversations WHERE conversation_id = ?", (conversation_id,)
        ).fetchone()
        if row is None:
            return Conversation(conversation_id, False, False)
        return Conversation(conversation_id, bool(row[0]), bool(row[1]))

    def _upsert(self, conversation_id: int, column: str) -> None:
        self._db.execute("INSERT OR IGNORE INTO conversations (conversation_id) VALUES (?)", (conversation_id,))
        self._db.execute(f"UPDATE conversations SET {column} = 1 WHERE conversation_id = ?", (conversation_id,))
        self._db.commit()

    def mark_lead(self, conversation_id: int) -> None:
        self._upsert(conversation_id, "lead_created")

    def mark_handed_off(self, conversation_id: int) -> None:
        self._upsert(conversation_id, "handed_off")

    def add_message(self, conversation_id: int, role: str, content: str, now: float | None = None) -> None:
        """Keep one chat turn. Drops this chat's turns past the cap, and every chat's turns past their age."""
        now = time.time() if now is None else now
        self._db.execute(
            "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (conversation_id, role, content, now),
        )
        self._db.execute(
            "DELETE FROM messages WHERE conversation_id = ? AND id NOT IN "
            "(SELECT id FROM messages WHERE conversation_id = ? ORDER BY id DESC LIMIT ?)",
            (conversation_id, conversation_id, CHAT_KEEP_MESSAGES),
        )
        self._db.execute("DELETE FROM messages WHERE created_at < ?", (now - CHAT_KEEP_DAYS * 86_400,))
        self._db.commit()

    def history(self, conversation_id: int, limit: int = 12) -> list[dict[str, str]]:
        """This chat's most recent turns, oldest first, as the model takes them."""
        rows = self._db.execute(
            "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id DESC LIMIT ?",
            (conversation_id, limit),
        ).fetchall()
        return [{"role": role, "content": content} for role, content in reversed(rows)]

    def forget_conversation(self, conversation_id: int) -> None:
        """Delete everything kept here about one chat, including a lead still waiting to be filed."""
        self._db.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        self._db.execute("DELETE FROM conversations WHERE conversation_id = ?", (conversation_id,))
        self._db.execute(
            "DELETE FROM pending WHERE json_extract(payload, '$.conversation_id') = ?", (conversation_id,)
        )
        self._db.commit()

    def add_pending(self, kind: str, payload: dict[str, Any]) -> None:
        self._db.execute(
            "INSERT INTO pending (kind, payload, created_at) VALUES (?, ?, ?)", (kind, json.dumps(payload), time.time())
        )
        self._db.commit()

    def pending(self, limit: int = 20) -> list[PendingItem]:
        rows = self._db.execute("SELECT id, kind, payload, attempts FROM pending ORDER BY id LIMIT ?", (limit,)).fetchall()
        return [PendingItem(r[0], r[1], json.loads(r[2]), r[3]) for r in rows]

    def bump(self, item_id: int) -> None:
        self._db.execute("UPDATE pending SET attempts = attempts + 1 WHERE id = ?", (item_id,))
        self._db.commit()

    def remove(self, item_id: int) -> None:
        self._db.execute("DELETE FROM pending WHERE id = ?", (item_id,))
        self._db.commit()
