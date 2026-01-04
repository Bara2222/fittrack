from logging.config import fileConfig
import os
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Load .env so DATABASE_URL is available when running Alembic
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Resolve DB URL: prefer env, else point to instance/db.sqlite3 absolute path
base_dir = Path(__file__).resolve().parent.parent
instance_db = base_dir / 'instance' / 'db.sqlite3'
instance_db.parent.mkdir(parents=True, exist_ok=True)
url_from_env = os.getenv('DATABASE_URL')
resolved_url = url_from_env or f"sqlite:///{instance_db}"
config.set_main_option("sqlalchemy.url", resolved_url)

# No autogenerate metadata needed for upgrades already created
target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
