
"""Run Alembic with migrations provided by installed FZM packages."""

from importlib.metadata import entry_points
from pathlib import Path

from alembic import command
from alembic.config import Config


MIGRATIONS_GROUP = "fzm_alembic.migrations"


def get_migration_paths() -> list[Path]:
    """Discover migration directories registered by installed packages."""
    paths: list[Path] = []

    for entry_point in sorted(
        entry_points(group=MIGRATIONS_GROUP),
        key=lambda item: item.name,
    ):
        package = entry_point.load()
        path = Path(package.__file__).resolve().parent / "versions"

        if not path.is_dir():
            raise FileNotFoundError(
                f"Migration directory not found for {entry_point.name}: {path}"
            )

        paths.append(path)

    return paths


def create_config(database_url: str) -> Config:
    """Build an Alembic configuration for installed FZM packages."""
    migrations_path = Path(__file__).resolve().parent

    config = Config()
    config.set_main_option("script_location", str(migrations_path))
    config.set_main_option("sqlalchemy.url", database_url)
    config.set_main_option("path_separator", "newline")

    migration_paths = get_migration_paths()

    if not migration_paths:
        raise RuntimeError("No FZM migration packages are installed")

    config.set_main_option(
        "version_locations",
        "\n".join(str(path) for path in migration_paths),
    )

    return config


def upgrade(database_url: str, revision: str = "heads") -> None:
    """Upgrade all installed migration branches."""
    command.upgrade(create_config(database_url), revision)


def downgrade(database_url: str, revision: str) -> None:
    """Downgrade the database to the specified revision."""
    command.downgrade(create_config(database_url), revision)


def current(database_url: str) -> None:
    """Display the current database revisions."""
    command.current(create_config(database_url), verbose=True)


def heads(database_url: str) -> None:
    """Display the heads of all installed migration branches."""
    command.heads(create_config(database_url), verbose=True)
