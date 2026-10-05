from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from fzm_staking.orm.near.snapshot import Snapshot
from fzm_staking.orm.near.snapshot_metadata import SnapshotMetadata


class SnapshotRepository:
    """Provides synchronous database operations for NEAR staking snapshots."""

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

    def get(
        self,
        metadata: SnapshotMetadata,
        block_height: int,
    ) -> Snapshot | None:
        """
        Returns a staking snapshot by its snapshot metadata and block height.

        Args:
            metadata: Snapshot metadata containing the account and pool keys.
            block_height: Block height of the staking snapshot.

        Returns:
            The staking snapshot or `None` if it does not exist.
        """
        return self._session.get(
            Snapshot,
            (metadata.account_key, metadata.pool_key, block_height),
        )

    def add(self, snapshot: Snapshot) -> None:
        """
        Adds a staking snapshot to the current database session.

        Args:
            snapshot: Staking snapshot to add.
        """
        self._session.add(snapshot)

    def flush(self) -> None:
        """Flushes pending changes to the database."""
        self._session.flush()

    def safe_add(self, snapshot: Snapshot) -> bool:
        """
        Adds and flushes a staking snapshot within a savepoint.

        If an integrity conflict occurs,
        the savepoint is rolled back
        without rolling back the surrounding transaction.

        Args:
            snapshot: Staking snapshot to add.

        Returns:
            `True` if the staking snapshot was successfully flushed, otherwise `False`.
        """
        try:
            with self._session.begin_nested():
                # savepoint
                self.add(snapshot)
                self.flush()

            return True

        except IntegrityError:
            return False
