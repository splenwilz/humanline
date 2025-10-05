import asyncio
import sys
import os
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# Add the project root directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import our models and configuration
from core.database import Base
from core.config import settings
from models import user, onboarding  # Import all models to register them

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the database URL from our settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with provided connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    # Convert async URL to sync for Alembic if needed
    database_url = settings.database_url
    
    # Alembic needs sync drivers, so convert async URLs
    if "postgresql+asyncpg://" in database_url:
        sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    elif "sqlite+aiosqlite://" in database_url:
        sync_url = database_url.replace("sqlite+aiosqlite://", "sqlite://")
    else:
        sync_url = database_url
    
    # Create sync engine for Alembic
    from sqlalchemy import create_engine
    connectable = create_engine(sync_url)

    with connectable.connect() as connection:
        await asyncio.get_event_loop().run_in_executor(
            None, do_run_migrations, connection
        )

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Check if we're in an async context
    try:
        loop = asyncio.get_running_loop()
        # We're in an async context, run async migrations
        asyncio.create_task(run_async_migrations())
    except RuntimeError:
        # No running loop, use sync approach
        database_url = settings.database_url
        
        # Convert async URL to sync for Alembic
        if "postgresql+asyncpg://" in database_url:
            sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        elif "sqlite+aiosqlite://" in database_url:
            sync_url = database_url.replace("sqlite+aiosqlite://", "sqlite://")
        else:
            sync_url = database_url
        
        from sqlalchemy import create_engine
        connectable = create_engine(sync_url)

        with connectable.connect() as connection:
            do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()