"""
Rate-limiter middleware — sliding-window per-IP rate limiting.

Environment variables:
    RATE_LIMIT_RPM   — max requests per minute per IP (default: 120)
    RATE_LIMIT_BURST — burst allowance above RPM (default: 20)
"""

import os
import time
import threading
from collections import defaultdict

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

RATE_LIMIT_RPM = int(os.getenv("RATE_LIMIT_RPM", "120"))
RATE_LIMIT_BURST = int(os.getenv("RATE_LIMIT_BURST", "20"))
_WINDOW_SECONDS = 60

# Per-IP request timestamps
_buckets: dict[str, list[float]] = defaultdict(list)
_lock = threading.Lock()


def _client_ip(request: Request) -> str:
    """Extract the client IP, respecting X-Forwarded-For if present."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _prune_and_count(ip: str, now: float) -> int:
    """Remove expired timestamps and return the current count."""
    cutoff = now - _WINDOW_SECONDS
    timestamps = _buckets[ip]
    # Remove old entries
    _buckets[ip] = [t for t in timestamps if t > cutoff]
    return len(_buckets[ip])


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter that returns 429 when exceeded."""

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ("/api/v1/health", "/api/v1/health/ready"):
            return await call_next(request)

        ip = _client_ip(request)
        now = time.time()
        max_allowed = RATE_LIMIT_RPM + RATE_LIMIT_BURST

        with _lock:
            count = _prune_and_count(ip, now)
            if count >= max_allowed:
                retry_after = int(_WINDOW_SECONDS - (now - _buckets[ip][0])) + 1
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Rate limit exceeded. Please slow down.",
                        "retry_after_seconds": max(retry_after, 1),
                    },
                    headers={"Retry-After": str(max(retry_after, 1))},
                )
            _buckets[ip].append(now)

        response = await call_next(request)
        # Add rate-limit headers for transparency
        with _lock:
            remaining = max(0, max_allowed - len(_buckets[ip]))
        response.headers["X-RateLimit-Limit"] = str(max_allowed)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
