"""Alembic environment configuration for async SQLAlchemy.

This env.py is configured to work with Cortex's async SQLAlchemy engine
and schema-per-tenant isolation. When running migrations, Alembic will
connect using an async driver (asyncpg) and target the metadata from
db.base.Base.
"""

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

# Alembic Config object
config = context.config

# Interpret config for logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url from DATABASE_URL environment variable
database_url = os.getenv("DATABASE_URL", "")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Import Base metadata for autogenerate support
from db.base import Base  # noqa: E402

target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Execute migrations in the given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode using an async engine.

    Creates an async engine from the configured URL and runs migrations
    within a connection. This is used when running `alembic upgrade head`.
    """
    configuration = config.get_section(config.config_ini_section, {})
    url = config.get_main_option("sqlalchemy.url")

    connectable = create_async_engine(
        url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
