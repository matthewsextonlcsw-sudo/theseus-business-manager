"""Local state in SQLite: which chats have a lead or were handed off, and work waiting to be retried.

Nothing a visitor sends is lost if Twenty or the model is down: it waits here and is retried.
"""
from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
