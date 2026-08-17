"""ASGI middleware enforcing Clerk authentication on all /api/v1/* routes."""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse

from auth.clerk import ClerkAuthError, ClerkVerifier, user_from_claims

API_V1_PREFIX = "/api/v1"


class AuthMiddleware:
    """Validate the Clerk session token on every /api/v1/* request.

    On success, stores ``user`` and ``tenant_id`` in ``request.state`` (via
    the ASGI scope state). The tenant context is then applied to database
    sessions by the ``get_tenant_session`` dependency so every query runs
    inside the tenant's isolated PostgreSQL schema.

    Public paths (/health, OpenAPI docs) and CORS preflight requests pass
    through unauthenticated.
    """

    def __init__(self, app, verifier: ClerkVerifier | None = None):
        self.app = app
        self.verifier = verifier or ClerkVerifier.from_settings()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope["path"]
        is_api = path == API_V1_PREFIX or path.startswith(API_V1_PREFIX + "/")
        # OPTIONS preflight is handled by the CORS middleware (outermost).
        if not is_api or scope.get("method") == "OPTIONS":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        auth_header = request.headers.get("authorization", "")
        scheme, _, token = auth_header.partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            await self._reject(
                scope, receive, send,
                status_code=401,
                detail="Missing or invalid Authorization header",
            )
            return

        try:
            claims = self.verifier.verify(token.strip())
        except ClerkAuthError as exc:
            await self._reject(scope, receive, send, exc.status_code, exc.detail)
            return

        state = scope.setdefault("state", {})
        state["user"] = user_from_claims(claims)
        state["tenant_id"] = claims["org_id"]
        await self.app(scope, receive, send)

    async def _reject(self, scope, receive, send, status_code: int, detail: str):
        response = JSONResponse({"detail": detail}, status_code=status_code)
        if status_code == 401:
            response.headers["WWW-Authenticate"] = "Bearer"
        await response(scope, receive, send)
