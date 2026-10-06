from sqlalchemy import Integer, func, type_coerce
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from fzm_staking.orm.near.snapshot import Snapshot
from fzm_staking.orm.near.key import Key


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
        key: Key,
        block_height: int,
    ) -> Snapshot | None:
        """
        Returns a staking snapshot by its snapshot key and block height.

        Args:
            key: Staking relationship key.
            block_height: Block height of the staking snapshot.

        Returns:
            The staking snapshot or `None` if it does not exist.
        """
        return self._session.get(
            Snapshot,
            (key.account_key, key.pool_key, block_height),
        )

    def get_latest(self, key: Key) -> Snapshot | None:
        """
        Returns the latest staking snapshot for a key.

        Args:
            key: Staking relationship key.

        Returns:
            The snapshot with the greatest block height,
            or `None` if none exists.
        """
        statement = select(
            type_coerce(
                func.max(Snapshot.block_height),
                Integer,
            )
        ).where(
            Snapshot.account_key == key.account_key,
            Snapshot.pool_key == key.pool_key,
        )

        block_height: int | None = self._session.exec(statement).one()

        if block_height is None:
            return None

        return self.get(key, block_height)


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
