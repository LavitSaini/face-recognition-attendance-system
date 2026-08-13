from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.models import Base
from app.config import DATABASE_URL


# Alembic Config object
config = context.config


# Configure Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# SQLAlchemy metadata
# Alembic uses this to detect changes in our models.
target_metadata = Base.metadata


# ------------------------------------------------------------
# OFFLINE MIGRATIONS
# ------------------------------------------------------------

def run_migrations_offline() -> None:
    """
    Run migrations in offline mode.

    This generates SQL statements without creating
    a database connection.
    """

    config.set_main_option(
        "sqlalchemy.url",
        DATABASE_URL
    )

    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()


# ------------------------------------------------------------
# ONLINE MIGRATIONS
# ------------------------------------------------------------

def run_migrations_online() -> None:
    """
    Run migrations in online mode.

    This creates a real connection to Neon PostgreSQL
    and applies the migrations.
    """

    # Use DATABASE_URL from .env
    config.set_main_option(
        "sqlalchemy.url",
        DATABASE_URL
    )

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# ------------------------------------------------------------
# START MIGRATION
# ------------------------------------------------------------

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()
