from sqlalchemy import update, CursorResult
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col

from fzm_near.orm.staking.key import Key
from fzm_near.orm.staking.snapshot_search import SnapshotSearch
from fzm_near.sync_repositories.staking.errors import SnapshotSearchRepositoryError


class SearchRepository:
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
        Atomically locks the staking snapshot search for the given key.

        Args:
            key: Staking relationship key.

        Returns:
            `True` if the staking snapshot search was successfully locked.
            `False` if it was already locked or does not exist.
        """

        statement =(
            update(SnapshotSearch)
            .where(
                col(SnapshotSearch.account_key) == key.account_key,
                col(SnapshotSearch.pool_key) == key.pool_key,
                col(SnapshotSearch.is_locked).is_(False)
            )
            .values(is_locked=True)
        )

        result: CursorResult = self._session.exec(statement)
        return result.rowcount == 1

    def unlock(self, key: Key) -> None:
        """
        Unlocks the staking snapshot search for the given key.

        Args:
            key: Staking relationship key.
        """

        statement = (
            update(SnapshotSearch)
            .where(
                col(SnapshotSearch.account_key) == key.account_key,
                col(SnapshotSearch.pool_key) == key.pool_key,
            )
            .values(is_locked=False)
        )

        self._session.exec(statement)

    def get(self, key: Key) -> SnapshotSearch | None:
        """
        Returns the staking snapshot search for a key.

        Args:
            key: Staking relationship key.

        Returns:
            The staking snapshot search or `None` if it does not exist.
        """
        return self._session.get(
            SnapshotSearch, (key.account_key, key.pool_key)
        )

    def add(self, search: SnapshotSearch) -> None:
        """
        Adds a staking snapshot search to the current database session.

        Args:
            search: Staking snapshot search to add.
        """
        self._session.add(search)

    def update(
        self,
        search: SnapshotSearch,
        up_to_block_height: int,
        is_reward_tracking_active: bool,
    ) -> None:
        """
        Updates the staking snapshot search progress and reward-tracking state.

        Args:
            search: Staking snapshot search to update.
            up_to_block_height: Inclusive upper boundary of the processed range.
            is_reward_tracking_active:
                Whether reward tracking remains active after the processed range.
        """

        if not search.is_locked:
            raise SnapshotSearchRepositoryError(
                "Staking snapshot search is not locked to update for key: %s",
                Key(
                    account_key=search.account_key,
                    pool_key=search.pool_key,
                ),
            )

        if (
                search.up_to_block_height is not None
                and up_to_block_height < search.up_to_block_height
        ):
            raise SnapshotSearchRepositoryError(
                f"`up_to_block_height` must not decrease for key: %s",
                Key(
                    account_key=search.account_key,
                    pool_key=search.pool_key,
                ),
            )

        search.up_to_block_height = up_to_block_height
        search.is_reward_tracking_active = is_reward_tracking_active

        self._session.add(search)

    def flush(self) -> None:
        """Flushes pending changes to the database."""
        self._session.flush()

    def safe_add(self, search: SnapshotSearch) -> SnapshotSearch:
        """
        Adds and flushes a staking snapshot search within a savepoint.

        If an integrity conflict occurs, the savepoint is rolled back
        without rolling back the surrounding transaction.

        Args:
            search: Staking snapshot search to add.

        Returns:
            The added staking snapshot search.

        Raises:
            StakingSearchRepositoryError:
                If the staking snapshot search could not be added.
        """
        try:
            with self._session.begin_nested():
                # savepoint
                self.add(search)
                self.flush()

            return search


        except IntegrityError as e:
            raise SnapshotSearchRepositoryError(
                "Cannot add staking snapshot search for key: %s",
                Key(
                    account_key=search.account_key,
                    pool_key=search.pool_key,
                ),
            ) from e

