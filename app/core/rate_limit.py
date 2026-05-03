from __future__ import annotations

import ipaddress
import logging
import time

from fastapi import HTTPException, Request

from .config import settings

logger = logging.getLogger(__name__)

_LOCAL_HOSTS: frozenset[str] = frozenset(
    {"127.0.0.1", "::1", "localhost"}
)

_PRIVATE_NETWORKS: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...] = (
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
)

_UNLIMITED_PATHS: frozenset[str] = frozenset({
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/dashboard",
    "/v1/engine/query",
    "/v1/engine/briefing",
    "/v1/engine/scenario/info",
    "/v1/engine/scenario/stimuli",
    "/v1/engine/state",
    "/v1/engine/contacts",
    "/v1/engine/threats",
    "/v1/engine/coas",
    "/v1/engine/recommendation",
    "/v1/engine/analysis",
    "/v1/engine/assets",
    "/v1/engine/llm/health",
})

_STREAM_PREFIXES: tuple[str, ...] = (
    "/v1/engine/ws/",
    "/v1/stream/",
)


def is_local_request(request: Request) -> bool:
    host = request.client.host if request.client else ""
    if host in _LOCAL_HOSTS:
        return True
    return _is_private_ip(host)


def _is_private_ip(host: str) -> bool:
    try:
        addr = ipaddress.ip_address(host)
        return any(addr in net for net in _PRIVATE_NETWORKS)
    except ValueError:
        return False


def is_demo_skip_path(path: str) -> bool:
    if path in _UNLIMITED_PATHS:
        return True
    return path.startswith(_STREAM_PREFIXES)


class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60) -> None:
        self._max = max_requests
        self._window = window_seconds
        self._hits: dict[str, list[float]] = __import__("collections").defaultdict(list)

    def check(self, client_id: str, path: str = "") -> None:
        now = time.time()
        cutoff = now - self._window
        self._hits[client_id] = [t for t in self._hits[client_id] if t > cutoff]
        if len(self._hits[client_id]) >= self._max:
            logger.warning(
                "Rate limit blocked: client=%s path=%s hits=%d/%d",
                client_id, path, len(self._hits[client_id]), self._max,
            )
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        self._hits[client_id].append(now)


_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(max_requests=settings.rate_limit_per_minute)
    return _rate_limiter
