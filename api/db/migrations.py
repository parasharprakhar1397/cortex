"""All-or-nothing migration runner for schema-per-tenant isolation.

CRITICAL: If any tenant schema migration fails, ALL schemas are rolled back.
This ensures every tenant is at the same schema version.
"""

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_all_tenant_schemas(session: AsyncSession) -> list[str]:
    """Get list of all tenant_* schemas in the database."""
    result = await session.execute(
        text(
            "SELECT schema_name FROM information_schema.schemata "
            "WHERE schema_name LIKE 'tenant_%'"
        )
    )
    return [row[0] for row in result.fetchall()]


async def migrate_all_tenants(session: AsyncSession, alembic_cfg: Config):
    """Run pending migrations on all tenant schemas.

    Uses all-or-nothing semantics: if migration fails on any schema,
    all previously migrated schemas are rolled back to maintain consistency.

    Args:
        session: An active async database session.
        alembic_cfg: A configured Alembic Config object pointing to the
                     correct alembic.ini and env.py.

    Raises:
        Exception: Re-raises the migration failure after rolling back
                   all affected schemas.
    """
    schemas = await get_all_tenant_schemas(session)
    migrated: list[str] = []

    try:
        for schema in schemas:
            await session.execute(text(f"SET search_path TO {schema}"))
            command.upgrade(alembic_cfg, "head")
            migrated.append(schema)
    except Exception:
        # Roll back all schemas that were already migrated
        for schema in migrated:
            await session.execute(text(f"SET search_path TO {schema}"))
            command.downgrade(alembic_cfg, "-1")
        raise
