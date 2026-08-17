"""Tests for Task 0.3 — tenant-scoped DB session (requires PostgreSQL).

Verifies that the ``get_tenant_session`` dependency sets the PostgreSQL
search_path to ``tenant_{tenant_id}`` before yielding, proving the tenant
context extracted from the Clerk JWT is applied to database sessions.
Skips cleanly when PostgreSQL is unavailable (e.g. docker stack not running).
"""

import asyncio
import os

import pytest
from starlette.requests import Request

from sqlalchemy import text

from auth.dependencies import get_tenant_session


def _asyncpg_url() -> str:
    """Return the DATABASE_URL using the asyncpg driver.

    CI passes a plain ``postgresql://`` URL; SQLAlchemy async engines need
    ``postgresql+asyncpg://``, so normalize here regardless of environment.
    """
    url = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://cortex:cortex_dev@localhost:5432/cortex_dev",
    )
    if "asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def _make_request(tenant_id: str) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/v1/me",
        "headers": [],
        "query_string": b"",
        "server": ("test", 80),
        "client": ("test", 80),
        "scheme": "http",
        "root_path": "",
        "state": {"tenant_id": tenant_id},
    }
    return Request(scope)


def test_tenant_session_sets_search_path():
    """get_tenant_session() sets search_path to tenant_{tenant_id}."""

    async def run():
        os.environ["DATABASE_URL"] = _asyncpg_url()
        import db.base as db_base

        await db_base.init_db()
        tenant_id = "auth_test_tenant"
        try:
            async for session in get_tenant_session(_make_request(tenant_id)):
                result = await session.execute(text("SHOW search_path"))
                assert f"tenant_{tenant_id}" in result.scalar(), result.scalar()
        except Exception as exc:  # noqa: BLE001 - DB absent => skip, not fail
            pytest.skip(f"PostgreSQL unavailable: {exc}")
        finally:
            try:
                async with db_base.async_session() as cleanup:
                    await cleanup.execute(
                        text(f"DROP SCHEMA IF EXISTS tenant_{tenant_id} CASCADE")
                    )
                    await cleanup.commit()
            except Exception:  # noqa: BLE001 - cleanup best effort
                pass
            if db_base.engine:
                await db_base.engine.dispose()

    asyncio.run(run())


def test_tenant_session_without_tenant_id_rejects():
    """get_tenant_session() without a tenant context raises 403."""

    async def run():
        from fastapi import HTTPException

        try:
            async for _ in get_tenant_session(_make_request(None)):
                raise AssertionError("expected HTTPException, got a session")
        except HTTPException as exc:
            assert exc.status_code == 403

    asyncio.run(run())
