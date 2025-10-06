from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Make sure this import path is correct relative to the 'migrations' folder
# It needs to go up one level to the 'backend' folder, then into 'app'
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__))))

# Now, import your Base from your models file
from app.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
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


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # This block is needed to get the DATABASE_URL from your environment variables on Render
    import os
    from dotenv import load_dotenv
    # We construct the path to the .env file in the 'backend' directory
    dotenv_path = os.path.join(dirname(dirname(abspath(__file__))), '.env')
    load_dotenv(dotenv_path=dotenv_path)
    
    # We will manually set the sqlalchemy.url for Alembic
    # It will use the DATABASE_URL from your Render environment variables
    alembic_config = config.get_section(config.config_ini_section, {})
    # Fallback to a local URL if DATABASE_URL is not set
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        alembic_config['sqlalchemy.url'] = db_url
    
    connectable = engine_from_config(
        alembic_config,
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

