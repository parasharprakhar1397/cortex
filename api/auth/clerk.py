"""Clerk JWT verification.

Validates Clerk session tokens (RS256 JWTs) against Clerk's published JWKS,
extracts identity claims, and maps them onto the Cortex user model.

Design notes:
- No live Clerk instance exists yet, so the JWKS source is injectable. Tests
  validate against locally generated RSA keys via a static in-memory client
  (see ``tests/auth_test_utils.py``) — no network access required.
- The ``audience`` check is only enforced when an audience is configured;
  Clerk session tokens are normally validated by signature, issuer, and
  expiry, so ``audience`` defaults to unset (skipped).
"""

from __future__ import annotations

import jwt

from app.config import Settings, get_settings


class ClerkAuthError(Exception):
    """Base class for authentication failures.

    ``status_code`` drives the HTTP response the middleware returns.
    """

    status_code = 401

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class ClerkInvalidTokenError(ClerkAuthError):
    """Token is missing, malformed, expired, or fails signature/issuer checks."""

    status_code = 401


class ClerkMissingOrgError(ClerkAuthError):
    """Token is valid but carries no ``org_id`` (user belongs to no practice)."""

    status_code = 403


class ClerkVerifier:
    """Verifies Clerk session tokens against a JWKS source."""

    def __init__(
        self,
        *,
        jwks_client: jwt.PyJWKClient | None = None,
        jwks_url: str | None = None,
        issuer: str | None = None,
        audience: str | None = None,
        leeway: int = 10,
    ):
        if jwks_client is None:
            if not jwks_url:
                raise ValueError("Either jwks_client or jwks_url is required")
            jwks_client = jwt.PyJWKClient(jwks_url, cache_keys=True)
        self._jwks_client = jwks_client
        self.issuer = issuer or None
        self.audience = audience or None
        self.leeway = leeway

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> "ClerkVerifier":
        settings = settings or get_settings()
        return cls(
            jwks_url=settings.clerk_jwks_url or None,
            issuer=settings.clerk_issuer or None,
        )

    def verify(self, token: str) -> dict:
        """Validate a Clerk session token and return its verified claims.

        Raises:
            ClerkInvalidTokenError: token missing, malformed, expired, or fails
                signature/issuer validation (HTTP 401).
            ClerkMissingOrgError: token is valid but the user has no active
                organization (no ``org_id`` claim) (HTTP 403).
        """
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)
        except (jwt.PyJWKClientError, jwt.InvalidTokenError) as exc:
            raise ClerkInvalidTokenError(
                "Token signing key could not be resolved"
            ) from exc

        try:
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=self.issuer,
                audience=self.audience,
                options={"verify_aud": bool(self.audience)},
                leeway=self.leeway,
            )
        except jwt.ExpiredSignatureError as exc:
            raise ClerkInvalidTokenError("Token has expired") from exc
        except jwt.InvalidTokenError as exc:
            raise ClerkInvalidTokenError("Token is invalid") from exc

        if not claims.get("sub"):
            raise ClerkInvalidTokenError("Token is missing the subject (sub) claim")
        if not claims.get("org_id"):
            raise ClerkMissingOrgError(
                "User does not belong to a practice (org_id claim missing); "
                "create or select an organization in Clerk"
            )
        return claims


def user_from_claims(claims: dict) -> dict:
    """Map verified Clerk JWT claims onto the Cortex user shape.

    Returns a dict with ``sub``/``email``/``org_id``/``role`` suitable for
    ``request.state.user``. ``role`` is the raw Clerk ``org_role`` claim
    (e.g. ``org:admin`` / ``org:member``).
    """
    return {
        "sub": claims.get("sub"),
        "email": claims.get("email", ""),
        "org_id": claims.get("org_id"),
        "role": claims.get("org_role", ""),
    }
