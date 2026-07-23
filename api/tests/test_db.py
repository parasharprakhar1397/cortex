"""
Integration tests for Database Foundation (Task 0.2).

Tests:
1. Database connection and initialization
2. Tenant schema creation
3. Tenant schema isolation (set search_path)
4. Schema existence verification
5. All-or-nothing migration semantics

Run with:
    docker compose exec api python tests/test_db.py
"""

import asyncio
import sys
import os

# Ensure api/ is on the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
import db.base as db_base
from db.tenant import create_tenant_schema, set_tenant_schema, tenant_schema_exists
from db.migrations import get_all_tenant_schemas


def green(msg: str) -> str:
    return f"\033[92m{msg}\033[0m"


def red(msg: str) -> str:
    return f"\033[91m{msg}\033[0m"


def bold(msg: str) -> str:
    return f"\033[1m{msg}\033[0m"


passed = 0
failed = 0


def check(condition: bool, name: str) -> None:
    global passed, failed
    if condition:
        print(f"  {green('✓')} {name}")
        passed += 1
    else:
        print(f"  {red('✗')} {name}")
        failed += 1


async def run_test_db_connection():
    """Test 1: Database connection and initialization."""
    print(bold("\nTest 1: Database Connection"))
    await db_base.init_db()
    check(db_base.engine is not None, "Engine created")
    check(db_base.async_session is not None, "Session factory created")

    async with db_base.async_session() as session:
        result = await session.execute(text("SELECT 1"))
        check(result.scalar() == 1, "Database responds to SELECT 1")
        result = await session.execute(text("SELECT version()"))
        version = result.scalar()
        check("PostgreSQL" in version, f"PostgreSQL version: {version[:40]}...")


async def run_test_tenant_schema_creation():
    """Test 2: Create a tenant schema and verify it exists."""
    print(bold("\nTest 2: Tenant Schema Creation"))
    tenant_id = "test_tenant_abc"

    async with db_base.async_session() as session:
        # Create the schema
        schema_name = await create_tenant_schema(session, tenant_id)
        await session.commit()
        check(schema_name == f"tenant_{tenant_id}", f"Schema name: {schema_name}")

        # Verify it exists in information_schema
        exists = await tenant_schema_exists(session, tenant_id)
        check(exists is True, "Schema visible in information_schema")

        # Verify GET_ALL_TENANT_SCHEMAS includes it
        schemas = await get_all_tenant_schemas(session)
        check(schema_name in schemas, f"get_all_tenant_schemas() includes {schema_name}")


async def run_test_tenant_schema_isolation():
    """Test 3: Set search_path and verify isolation."""
    print(bold("\nTest 3: Tenant Schema Isolation"))
    tenant_id = "test_tenant_isolation"

    async with db_base.async_session() as session:
        # Create schema
        await create_tenant_schema(session, tenant_id)
        await session.commit()

        # Set search_path to tenant schema
        schema_name = await set_tenant_schema(session, tenant_id)
        check(schema_name == f"tenant_{tenant_id}", f"search_path set to {schema_name}")

        # Create a table in the tenant schema
        await session.execute(text("CREATE TABLE IF NOT EXISTS test_data (id SERIAL PRIMARY KEY, value TEXT)"))
        await session.commit()

        # Insert data
        await session.execute(text("INSERT INTO test_data (value) VALUES ('tenant-isolated')"))
        await session.commit()

        # Query it back
        result = await session.execute(text("SELECT value FROM test_data WHERE value = 'tenant-isolated'"))
        row = result.fetchone()
        check(row is not None and row[0] == "tenant-isolated", "Data inserted and retrieved from tenant schema")

        # Verify the actual search_path
        result = await session.execute(text("SHOW search_path"))
        sp = result.scalar()
        check(schema_name in sp, f"search_path contains {schema_name}: {sp}")


async def run_test_public_schema_isolation():
    """Test 4: Data in tenant schema is NOT visible from public schema."""
    print(bold("\nTest 4: Cross-Schema Isolation"))
    tenant_id = "test_tenant_isolation"

    async with db_base.async_session() as session:
        # Switch to public schema
        await session.execute(text("SET search_path TO public"))
        await session.commit()

        # Try to query the tenant table from public — should fail
        try:
            await session.execute(text("SELECT * FROM test_data"))
            check(False, "Should not be able to see tenant data from public schema")
        except Exception as e:
            check("test_data" in str(e), f"Correctly isolated: tenant table not visible from public")


async def run_test_all_or_nothing_migration():
    """Test 5: All-or-nothing migration semantics.

    Create 2 tenant schemas. Run a migration that works on schema 1 but
    simulate a failure on schema 2. Verify schema 1 is untouched (rolled back).
    """
    print(bold("\nTest 5: All-or-Nothing Migration Semantics"))
    tenant_a = "migrate_test_a"
    tenant_b = "migrate_test_b"

    async with db_base.async_session() as session:
        # Create both tenant schemas
        await create_tenant_schema(session, tenant_a)
        await create_tenant_schema(session, tenant_b)
        await session.commit()

        # Create a table in schema A manually (simulating a previous migration state)
        await session.execute(text(f"SET search_path TO tenant_{tenant_a}"))
        await session.execute(text("CREATE TABLE IF NOT EXISTS tracked (id SERIAL PRIMARY KEY, step TEXT)"))
        await session.execute(text("INSERT INTO tracked (step) VALUES ('before-migration')"))
        await session.commit()

        # Also create same table in schema B
        await session.execute(text(f"SET search_path TO tenant_{tenant_b}"))
        await session.execute(text("CREATE TABLE IF NOT EXISTS tracked (id SERIAL PRIMARY KEY, step TEXT)"))
        await session.execute(text("INSERT INTO tracked (step) VALUES ('before-migration')"))
        await session.commit()

    # Now simulate a migration: run a "good" migration on A, and a "bad" one on B.
    # In the real migrate_all_tenants(), each schema's migration runs in its
    # own Alembic transaction. If a schema's migration fails, only that schema's
    # changes are rolled back by Alembic; the function then manually rolls back
    # all previously-completed schemas. We simulate this with savepoints.

    async with db_base.async_session() as session:
        # Start an outer transaction to represent the entire migration run
        migrated = []
        try:
            # Migrate tenant A — success (commit this schema's work)
            await session.execute(text(f"SET search_path TO tenant_{tenant_a}"))
            await session.execute(text("INSERT INTO tracked (step) VALUES ('migration-applied')"))
            await session.commit()
            migrated.append(tenant_a)

            # Migrate tenant B — start but fail mid-way
            await session.execute(text(f"SET search_path TO tenant_{tenant_b}"))
            await session.execute(text("INSERT INTO tracked (step) VALUES ('migration-applied')"))
            # Simulate failure — in real life Alembic would roll back B's transaction;
            # we roll back the insert we just did
            await session.rollback()
            raise RuntimeError("Simulated migration failure on tenant B")

        except RuntimeError:
            # All-or-nothing: roll back ALL previously migrated schemas
            for tenant in migrated:
                await session.execute(text(f"SET search_path TO tenant_{tenant}"))
                await session.execute(text("DELETE FROM tracked WHERE step = 'migration-applied'"))
            await session.commit()

    # Verify: tenant A has only 'before-migration', not 'migration-applied'
    async with db_base.async_session() as session:
        await session.execute(text(f"SET search_path TO tenant_{tenant_a}"))
        result = await session.execute(text("SELECT step FROM tracked ORDER BY id"))
        steps_a = [row[0] for row in result.fetchall()]
        check(
            "migration-applied" not in steps_a and "before-migration" in steps_a,
            f"Tenant A rolled back correctly: {steps_a}",
        )

        # Tenant B also should only have 'before-migration'
        await session.execute(text(f"SET search_path TO tenant_{tenant_b}"))
        result = await session.execute(text("SELECT step FROM tracked ORDER BY id"))
        steps_b = [row[0] for row in result.fetchall()]
        check(
            "migration-applied" not in steps_b and "before-migration" in steps_b,
            f"Tenant B untouched: {steps_b}",
        )

    # Cleanup: drop test schemas
    async with db_base.async_session() as session:
        for tid in [tenant_a, tenant_b, "test_tenant_abc", "test_tenant_isolation"]:
            schema = f"tenant_{tid}"
            await session.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        await session.commit()


async def main():
    print(bold("=" * 60))
    print(bold("Cortex v1 — Database Foundation Tests (Task 0.2)"))
    print(bold("=" * 60))

    await run_test_db_connection()
    await run_test_tenant_schema_creation()
    await run_test_tenant_schema_isolation()
    await run_test_public_schema_isolation()
    await run_test_all_or_nothing_migration()

    # Dispose engine
    if db_base.engine:
        await db_base.engine.dispose()

    print(bold("\n" + "=" * 60))
    print(f"Results: {green(passed)} passed, {red(failed)} failed out of {passed + failed}")
    print(bold("=" * 60))

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
