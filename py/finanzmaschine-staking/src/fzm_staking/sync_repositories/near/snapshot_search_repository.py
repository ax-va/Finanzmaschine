from sqlalchemy import delete
from sqlmodel import Session, select

from fzm_staking.orm.near.key import Key
from fzm_staking.orm.near.snapshot_search import SnapshotSearch


class SnapshotSearchRepository:
    """Provides synchronous database operations for snapshot searches."""

    def __init__(self, session: Session) -> None:
        """
        Args:
            session: Database session used for persistence operations.
        """
        self._session = session

    @property
    def session(self) -> Session:
        """Returns the database session used by the repository."""
        return self._session

    def get(self, key: Key) -> SnapshotSearch | None:
        """
        Returns the snapshot search for a key.

        Args:
            key: Staking relationship key.

        Returns:
            The snapshot search or `None` if does not exist.
        """
        return self._session.get(
            SnapshotSearch,
            (key.account_key, key.pool_key),
        )

    def add(self, search: SnapshotSearch) -> None:
        """
        Adds a snapshot search to the current database session.

        Args:
            search: Snapshot search to add.
        """
        self._session.add(search)

    def flush(self) -> None:
        """Flushes pending changes to the database."""
        self._session.flush()
