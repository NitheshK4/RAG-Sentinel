"""
Request-ID middleware — generates or propagates a unique X-Request-Id header
for every request to enable end-to-end traceability in logs.
"""

import uuid
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Attach a unique X-Request-Id to every request and response.
    If the client sends one, it is propagated; otherwise a UUID4 is generated.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())

        # Store on request state so downstream handlers can access it
        request.state.request_id = request_id

        logger.info(
            "request_start request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id

        logger.info(
            "request_end request_id=%s status=%s",
            request_id,
            response.status_code,
        )

        return response
