"""Helpers for exercising Clerk auth without a live Clerk instance.

Generates an RSA keypair locally, builds a matching JWKS, and signs
Clerk-shaped session tokens (RS256) so tests never touch the network.
"""

import base64
import time

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

TEST_ISSUER = "https://test-practice.clerk.accounts.dev"
TEST_KID = "test-signing-key"


def b64url_int(value: int) -> str:
    """Encode an integer as a base64url string (JWK n/e encoding)."""
    length = max(1, (value.bit_length() + 7) // 8)
    return base64.urlsafe_b64encode(value.to_bytes(length, "big")).rstrip(b"=").decode()


def make_keypair() -> tuple:
    """Generate an RSA keypair and the matching public JWK dict.

    Returns ``(private_key, public_jwk_dict)``.
    """
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pub_numbers = private_key.public_key().public_numbers()
    public_jwk = {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": TEST_KID,
        "n": b64url_int(pub_numbers.n),
        "e": b64url_int(pub_numbers.e),
    }
    return private_key, public_jwk


class StaticJWKSClient:
    """Minimal ``jwt.PyJWKClient``-compatible client backed by a JWKS dict.

    Implements ``get_signing_key_from_jwt(token)`` by resolving the ``kid``
    header against an in-memory key set, mirroring PyJWT's lookup so
    ``ClerkVerifier`` works unchanged.
    """

    def __init__(self, jwks_dict: dict):
        self._jwks = jwt.PyJWKSet.from_dict(jwks_dict)

    def get_signing_key_from_jwt(self, token: str):
        kid = jwt.get_unverified_header(token).get("kid")
        for key in self._jwks.keys:
            if key.key_id == kid:
                return key
        raise jwt.PyJWKClientError(
            f"Unable to find a signing key that matches: {kid}"
        )


def sign_token(
    private_key,
    *,
    sub: str = "user_2test123",
    email: str = "owner@smilecare.example",
    org_id: str | None = "org_practice_smilecare",
    org_role: str = "org:admin",
    issuer: str = TEST_ISSUER,
    expires_in: int = 3600,
    **extra_claims,
) -> str:
    """Sign a Clerk-shaped session token with the given private key.

    Pass ``org_id=None`` to mint a token without the ``org_id`` claim
    (simulates a user with no active organization).
    """
    now = int(time.time())
    claims = {
        "sub": sub,
        "email": email,
        "org_role": org_role,
        "iss": issuer,
        "iat": now,
        "nbf": now,
        "exp": now + expires_in,
        **extra_claims,
    }
    if org_id is not None:
        claims["org_id"] = org_id
    return jwt.encode(claims, private_key, algorithm="RS256", headers={"kid": TEST_KID})
