from __future__ import annotations

import time
from collections import defaultdict

from fastapi import HTTPException, Request

from .config import settings


class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60) -> None:
        self._max = max_requests
        self._window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def check(self, client_id: str) -> None:
        now = time.time()
        cutoff = now - self._window
        self._hits[client_id] = [t for t in self._hits[client_id] if t > cutoff]
        if len(self._hits[client_id]) >= self._max:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        self._hits[client_id].append(now)


_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(max_requests=settings.rate_limit_per_minute)
    return _rate_limiter
