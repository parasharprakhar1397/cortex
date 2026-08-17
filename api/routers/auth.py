"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user, get_tenant_id

router = APIRouter(prefix="/api/v1", tags=["auth"])


@router.get("/me")
async def me(
    user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """Return the authenticated user's identity and tenant context.

    AuthMiddleware has already validated the Clerk session token and set
    request.state.user/tenant_id; the dependencies surface them here.
    """
    return {
        "user_id": user["sub"],
        "email": user["email"],
        "tenant_id": tenant_id,
        "role": user["role"],
    }
