from __future__ import annotations

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

from .config import settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    request: Request,
    api_key: str | None = Security(_api_key_header),
) -> None:
    if not settings.api_key_auth_enabled:
        return
    valid_keys = {k.strip() for k in settings.api_keys_csv.split(",") if k.strip()}
    if not valid_keys:
        return
    if api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
