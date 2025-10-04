import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

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

# Set the database URL from our settings (convert async URL to sync for Alembic)
# Handle SSL parameters that are incompatible with psycopg2
sync_database_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")

# Remove SSL parameters that cause issues with psycopg2 in Alembic
# These parameters are valid for asyncpg but not for psycopg2
if "ssl=require" in sync_database_url:
    # Remove SSL parameters for local development
    # In production, SSL should be handled at the connection level
    sync_database_url = sync_database_url.split("?")[0]
    
config.set_main_option("sqlalchemy.url", sync_database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

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


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
