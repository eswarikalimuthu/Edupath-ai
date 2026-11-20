"""
EduPath AI - Sliding Window Rate Limiter (Pure ASGI)
Prevents DoS and brute-force attacks on sensitive endpoints.
"""

import time
from collections import defaultdict
from starlette.responses import JSONResponse
from backend.config import settings

class RateLimiterMiddleware:
    def __init__(self, app, max_requests_per_minute: int = None):
        self.app = app
        self.max_requests = max_requests_per_minute or settings.RATE_LIMIT_REQUESTS_PER_MINUTE
        self.requests_log = defaultdict(list)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        client_ip = "127.0.0.1"
        client = scope.get("client")
        if client:
            client_ip = client[0]

        now = time.time()
        window_start = now - 60.0
        self.requests_log[client_ip] = [t for t in self.requests_log[client_ip] if t > window_start]

        if len(self.requests_log[client_ip]) >= self.max_requests:
            response = JSONResponse(
                status_code=429,
                content={"error": "Too Many Requests", "detail": "Rate limit exceeded. Please try again after 60 seconds."}
            )
            await response(scope, receive, send)
            return

        self.requests_log[client_ip].append(now)
        await self.app(scope, receive, send)
