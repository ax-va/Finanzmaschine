from sqlalchemy import update, CursorResult
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col

from fzm_near.orm.staking_action_search import StakingActionSearch
from fzm_near.sync_repositories.staking_action_search_repository_error import StakingActionSearchRepositoryError


class StakingActionSearchRepository:
    """Provides synchronous database operations for NEAR staking action searches."""

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

    def lock(self, search: StakingActionSearch) -> None:
        """
        Atomically locks the action search for the given key.

        Args:
            search: Staking action search to update.
        """

        statement =(
            update(StakingActionSearch)
            .where(
                col(StakingActionSearch.account_key) == search.account_key,
                col(StakingActionSearch.locked).is_(False)
            )
            .values(locked=True)
        )

        result: CursorResult = self._session.exec(statement)
        
        if result.rowcount != 1:
            raise StakingActionSearchRepositoryError(
                f"Cannot lock action search for account key: {search.account_key}"
            )

        self._session.refresh(search)

    def unlock(self, search: StakingActionSearch) -> None:
        """
        Unlocks the action search for the given key.

        Args:
            search: Staking action search to update.
        """

        statement = (
            update(StakingActionSearch)
            .where(
                col(StakingActionSearch.account_key) == search.account_key,
            )
            .values(locked=False)
        )

        self._session.exec(statement)
        self._session.refresh(search)

    def get(self, account_key: str) -> StakingActionSearch | None:
        """
        Returns a staking action search by account key.

        Args:
            account_key: Account identifier.

        Returns:
            The staking action search or `None` if it does not exist.
        """
        return self._session.get(StakingActionSearch, account_key)

    def add(self, search: StakingActionSearch) -> None:
        """
        Adds a staking action search to the current database session.

        Args:
            search: Staking action search to add.
        """
        self._session.add(search)

    def safe_add(self, search: StakingActionSearch) -> None:
        """
        Adds and flushes a staking action search within a savepoint.

        If an integrity conflict occurs, the savepoint is rolled back
        without rolling back the surrounding transaction.

        Args:
            search: Staking action search to add.
        """
        try:
            with self._session.begin_nested():
                # savepoint
                self.add(search)
                self.flush()

        except IntegrityError:
            raise StakingActionSearchRepositoryError(
                f"Cannot add staking action search for account key: {search.account_key}"
            )

    def update(
        self,
        search: StakingActionSearch,
        up_to_tx_block_height: int,
    ) -> None:
        """
        Updates the upper transaction block height of a staking action search.

        Args:
            search: Staking action search to update.
            up_to_tx_block_height: New inclusive upper transaction block height.
        """
        if not search.locked:
            raise StakingActionSearchRepositoryError(
                f"Staking action search is not locked "
                f"to update for account key: {search.account_key}"
            )
        
        if (
            search.up_to_tx_block_height is not None
            and up_to_tx_block_height < search.up_to_tx_block_height
        ):
            raise StakingActionSearchRepositoryError(
                f"`up_to_tx_block_height` must not decrease "
                f"for account key: {search.account_key}"
            )

        search.up_to_tx_block_height = up_to_tx_block_height
        self._session.add(search)

    def flush(self) -> None:
        """Flushes pending changes to the database."""
        self._session.flush()
