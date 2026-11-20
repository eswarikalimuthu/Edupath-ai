"""
EduPath AI - Security Headers Middleware (Pure ASGI)
Attaches strict OWASP-recommended HTTP security response headers.
"""

class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-content-type-options", b"nosniff"))
                headers.append((b"x-frame-options", b"DENY"))
                headers.append((b"x-xss-protection", b"1; mode=block"))
                headers.append((b"strict-transport-security", b"max-age=31536000; includeSubDomains"))
                headers.append((b"referrer-policy", b"strict-origin-when-cross-origin"))
                headers.append((b"content-security-policy", b"default-src 'self'; frame-ancestors 'none';"))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_wrapper)
