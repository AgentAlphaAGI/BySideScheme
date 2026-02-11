import os
from typing import Optional

from fastapi import Header, HTTPException


def verify_api_key(x_api_key: Optional[str]) -> None:
    expected = os.getenv("LAISHIER_API_KEY")
    if not expected:
        return
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")


def require_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")) -> None:
    verify_api_key(x_api_key)
