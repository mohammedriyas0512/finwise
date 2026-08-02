"""
Small shared helpers used across routers.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal


def money(value) -> float:
    """Convert a Numeric/Decimal/str to a plain float for JSON responses."""
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def client_ip(request) -> str | None:
    """Best-effort client IP extraction (honours reverse-proxy headers)."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def month_key(dt: datetime) -> str:
    """Return 'YYYY-MM' for a datetime."""
    return dt.strftime("%Y-%m")
