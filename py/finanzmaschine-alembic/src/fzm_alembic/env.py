"""Configure Alembic for migrations from installed FZM packages."""

from importlib.metadata import entry_points
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel


config = context.config

if config.config_file_name is not None:
    if config.file_config.has_section("loggers"):
        fileConfig(config.config_file_name)


def load_models() -> None:
    """Import SQLModel models registered by installed FZM packages."""
    for entry_point in entry_points(group="fzm_alembic.models"):
        entry_point.load()


load_models()

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations without establishing a database connection."""
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
    """Run migrations using a database connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
