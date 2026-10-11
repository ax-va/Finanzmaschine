from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect

from fzm_alembic.runner import create_config, downgrade, upgrade


def test_near_migrations() -> None:
    """Verify NEAR migration discovery and revision chain integrity."""
    config = create_config("sqlite://")

    # Load the migration script directory from the Alembic configuration
    script = ScriptDirectory.from_config(config)

    # Collect all available migration revisions
    revisions = list(script.walk_revisions())

    # Extract revisions IDs for comparison with the expected set
    revision_ids = {revision.revision for revision in revisions}

    assert revision_ids == {
        "near_001",
        "near_002",
        "near_003",
        "near_004",
    }

    assert script.get_heads() == ["near_004"]


def test_near_upgrade(tmp_path) -> None:
    """Verify that upgrading creates all NEAR database tables."""
    database_url = f"sqlite:///{tmp_path / 'test.db'}"

    # Apply all migrations
    upgrade(database_url)

    engine = create_engine(database_url)
    try:
        tables = set(inspect(engine).get_table_names())

        assert {
            "alembic_version",
            "near_blocks",
            "near_staking_actions",
            "near_staking_snapshots",
            "near_staking_searches",
        } <= tables
    finally:
        engine.dispose()


def test_near_downgrade(tmp_path) -> None:
    """Verify that downgrading removes all NEAR database tables."""
    database_url = f"sqlite:///{tmp_path / 'test.db'}"

    # Apply all migrations to prepare the database for rollback
    upgrade(database_url)

    # Roll back all migrations to the base revision
    downgrade(database_url, "base")

    engine = create_engine(database_url)
    try:
        tables = set(inspect(engine).get_table_names())

        assert "near_blocks" not in tables
        assert "near_staking_actions" not in tables
        assert "near_staking_snapshots" not in tables
        assert "near_staking_searches" not in tables
    finally:
        engine.dispose()
