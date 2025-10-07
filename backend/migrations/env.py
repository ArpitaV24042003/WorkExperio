from logging.config import fileConfig
import sys
import os
from os.path import abspath, dirname
from app.database import Base  # Or wherever your SQLAlchemy Base is defined
from app import models  
from sqlalchemy import engine_from_config, pool
from alembic import context

# --- Import your models Base ---
# migrations → backend → app
sys.path.insert(0, dirname(dirname(abspath(__file__))))
from app.models import Base

# --- Alembic Config ---
config = context.config

# Set up Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for 'autogenerate' support
target_metadata = Base.metadata


def get_database_url() -> str:
    """Try multiple environment variable names for DB URL."""
    db_url = (
        os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("PGDATABASE_URL")
        or config.get_main_option("sqlalchemy.url")
    )
    if not db_url:
        raise RuntimeError("❌ No database URL found for Alembic migrations.")
    print(f"🔗 Alembic connecting to DB: {db_url}")
    return db_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    db_url = get_database_url()

    alembic_config = config.get_section(config.config_ini_section)
    alembic_config["sqlalchemy.url"] = db_url

    connectable = engine_from_config(
        alembic_config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
