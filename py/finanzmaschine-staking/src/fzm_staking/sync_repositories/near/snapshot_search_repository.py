from sqlalchemy import delete, update, CursorResult
from sqlmodel import Session, select, col

from fzm_staking.orm.near.key import Key
from fzm_staking.orm.near.search import SnapshotSearch


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

    def lock(self, key: Key) -> bool:
        """
        Atomically locks the snapshot search for the given key.

        Args:
            key: Staking relationship key.

        Returns:
            `True` if the snapshot search was successfully locked.
            `False` if it was already locked or does not exist.
        """

        statement =(
            update(SnapshotSearch)
            .where(
                col(SnapshotSearch.account_key) == key.account_key,
                col(SnapshotSearch.pool_key) == key.pool_key,
                col(SnapshotSearch.locked).is_(False)
            )
            .values(locked=True)
        )

        result: CursorResult = self._session.exec(statement)
        return result.rowcount == 1

    def unlock(self, key: Key) -> None:
        """
        Unlocks the snapshot search for the given key.

        Args:
            key: Staking relationship key.
        """

        statement = (
            update(SnapshotSearch)
            .where(
                col(SnapshotSearch.account_key) == key.account_key,
                col(SnapshotSearch.pool_key) == key.pool_key,
            )
            .values(locked=False)
        )

        self._session.exec(statement)

    def get(self, key: Key) -> SnapshotSearch | None:
        """
        Returns the snapshot search for a key.

        Args:
            key: Staking relationship key.

        Returns:
            The snapshot search or `None` if it does not exist.
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
