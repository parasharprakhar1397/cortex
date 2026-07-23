from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

PUBLIC_SCHEMA = "public"


async def set_tenant_schema(session: AsyncSession, tenant_id: str) -> str:
    """Set the PostgreSQL search_path to the tenant's schema.

    Creates the schema if it doesn't already exist, then sets search_path
    so all subsequent queries operate within that tenant's isolated namespace.

    Args:
        session: An active async database session.
        tenant_id: The tenant identifier (e.g., UUID or slug).

    Returns:
        The schema name that was set (tenant_{tenant_id}).
    """
    schema_name = f"tenant_{tenant_id}"
    await session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
    await session.execute(text(f"SET search_path TO {schema_name}"))
    return schema_name


async def create_tenant_schema(session: AsyncSession, tenant_id: str) -> str:
    """Create a new tenant schema without switching to it.

    Useful for provisioning schemas ahead of time (e.g., during onboarding)
    or for migration runners that iterate over schemas.

    Args:
        session: An active async database session.
        tenant_id: The tenant identifier.

    Returns:
        The schema name that was created (tenant_{tenant_id}).
    """
    schema_name = f"tenant_{tenant_id}"
    await session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
    return schema_name


async def tenant_schema_exists(session: AsyncSession, tenant_id: str) -> bool:
    """Check whether a tenant schema exists."""
    schema_name = f"tenant_{tenant_id}"
    result = await session.execute(
        text(
            "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = :name)"
        ),
        {"name": schema_name},
    )
    return result.scalar()
