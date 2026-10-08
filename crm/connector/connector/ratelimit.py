"""A small in-memory sliding-window limiter: at most N events per key in a time window."""
from __future__ import annotations

from collections import defaultdict, deque


class SlidingWindowLimiter:
    def __init__(self, max_events: int, window_s: float) -> None:
        self._max = max_events
        self._window = window_s
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, now: float) -> bool:
        events = self._events[key]
        while events and now - events[0] >= self._window:
            events.popleft()
        if len(events) >= self._max:
            return False
        events.append(now)
        return True
