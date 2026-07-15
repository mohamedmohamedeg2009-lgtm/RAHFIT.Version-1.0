from collections import defaultdict, deque
from time import monotonic

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.config import Settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory baseline; replace with Redis-backed limits before multi-instance deployment."""

    def __init__(self, app: object, settings: Settings) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self.settings = settings
        self.requests: defaultdict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client = request.client.host if request.client else "unknown"
        now = monotonic()
        window = self.requests[client]
        while window and now - window[0] >= self.settings.rate_limit_window_seconds:
            window.popleft()
        if len(window) >= self.settings.rate_limit_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded."
            )
        window.append(now)
        return await call_next(request)
