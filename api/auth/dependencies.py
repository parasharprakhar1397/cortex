"""FastAPI dependencies for authenticated, tenant-scoped access."""

from __future__ import annotations

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.tenant import set_tenant_schema


def get_current_user(request: Request) -> dict:
    """Return the authenticated user dict stored by AuthMiddleware.

    AuthMiddleware already guards every /api/v1 route; this dependency is
    defense-in-depth for endpoints that need the user explicitly.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_tenant_id(request: Request) -> str:
    """Return the tenant_id (Clerk org_id) for the current request."""
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to a practice (missing org_id)",
        )
    return tenant_id


async def get_tenant_session(request: Request) -> AsyncSession:
    """Yield an AsyncSession scoped to the request's tenant schema.

    Sets PostgreSQL search_path to ``tenant_{tenant_id}`` before yielding so
    every query in the request runs inside the tenant's isolated schema.
    Each request gets a fresh session (and thus a fresh connection), so the
    search_path cannot leak between requests.
    """
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenant context for this request",
        )

    # Imported at call time: init_db() reassigns the module-level factory at
    # app startup, so a top-level import would capture None.
    from db.base import async_session

    if async_session is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not initialized",
        )

    async with async_session() as session:
        await set_tenant_schema(session, tenant_id)
        yield session
