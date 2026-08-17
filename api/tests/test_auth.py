"""Tests for Task 0.3 — Clerk authentication (no live Clerk required).

All tokens are signed locally with a generated RSA keypair and verified
against a matching in-memory JWKS, so nothing touches the network.
"""

import pytest
from fastapi.testclient import TestClient

from auth.clerk import ClerkVerifier
from main import create_app

from tests.auth_test_utils import (
    StaticJWKSClient,
    TEST_ISSUER,
    make_keypair,
    sign_token,
)


@pytest.fixture(scope="module")
def keypair():
    """The shared (private_key, public_jwk) used for valid tokens."""
    return make_keypair()


@pytest.fixture(scope="module")
def verifier(keypair):
    _, public_jwk = keypair
    jwks_client = StaticJWKSClient({"keys": [public_jwk]})
    return ClerkVerifier(jwks_client=jwks_client, issuer=TEST_ISSUER)


@pytest.fixture(scope="module")
def client(verifier):
    return TestClient(create_app(verifier=verifier))


# ---------------------------------------------------------------------------
# Positive path
# ---------------------------------------------------------------------------

def test_verify_accepts_token_and_extracts_claims(verifier, keypair):
    private_key, _ = keypair
    claims = verifier.verify(sign_token(private_key))
    assert claims["sub"] == "user_2test123"
    assert claims["email"] == "owner@smilecare.example"
    assert claims["org_id"] == "org_practice_smilecare"
    assert claims["org_role"] == "org:admin"


def test_me_returns_claims(client, keypair):
    private_key, _ = keypair
    token = sign_token(private_key)
    resp = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == {
        "user_id": "user_2test123",
        "email": "owner@smilecare.example",
        "tenant_id": "org_practice_smilecare",
        "role": "org:admin",
    }


# ---------------------------------------------------------------------------
# Negative path: missing / malformed / expired / invalid tokens -> 401
# ---------------------------------------------------------------------------

def test_me_missing_token_returns_401(client):
    resp = client.get("/api/v1/me")
    assert resp.status_code == 401
    assert resp.headers.get("www-authenticate") == "Bearer"


def test_me_non_bearer_header_returns_401(client):
    resp = client.get("/api/v1/me", headers={"Authorization": "Basic abc123"})
    assert resp.status_code == 401


def test_me_malformed_token_returns_401(client):
    resp = client.get("/api/v1/me", headers={"Authorization": "Bearer not.a.jwt"})
    assert resp.status_code == 401


def test_me_expired_token_returns_401(client, keypair):
    private_key, _ = keypair
    token = sign_token(private_key, expires_in=-3600)
    resp = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


def test_me_token_signed_with_wrong_key_returns_401(client):
    # A different keypair -> signature won't verify against the JWKS.
    other_private, _ = make_keypair()
    token = sign_token(other_private)
    resp = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


def test_me_wrong_issuer_returns_401(client, keypair):
    private_key, _ = keypair
    token = sign_token(private_key, issuer="https://evil.example")
    resp = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Valid token without org_id -> 403
# ---------------------------------------------------------------------------

def test_me_token_without_org_id_returns_403(client, keypair):
    private_key, _ = keypair
    token = sign_token(private_key, org_id=None)
    resp = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
    assert "practice" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Public surface stays public
# ---------------------------------------------------------------------------

def test_health_is_unauthenticated(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "version": "0.1.0"}


def test_openapi_docs_are_unauthenticated(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
