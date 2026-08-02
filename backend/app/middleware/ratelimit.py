"""
In-memory sliding-window rate limiter (per client IP).

Lightweight and dependency-free. For multi-process / production deployments,
swap this for a Redis-backed limiter; the interface stays the same.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import RATE_LIMIT_PER_MINUTE


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = RATE_LIMIT_PER_MINUTE, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.hits: defaultdict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for docs/health/static.
        path = request.url.path
        if path in ("/docs", "/redoc", "/openapi.json", "/health", "/"):
            return await call_next(request)

        ident = request.client.host if request.client else "unknown"
        now = time.time()
        bucket = self.hits[ident]
        while bucket and bucket[0] <= now - self.window:
            bucket.popleft()
        if len(bucket) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
            )
        bucket.append(now)
        return await call_next(request)
