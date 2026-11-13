from sqlalchemy import update, CursorResult
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col

from fzm_near.orm.function_call.action_search import ActionSearch
from fzm_near.sync_repositories.function_call.errors import ActionSearchRepositoryError


class ActionSearchRepository:
    """Provides synchronous database operations for NEAR function call action searches."""

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

    def lock(self, search: ActionSearch) -> bool:
        """
        Atomically locks the function call action search.

        Args:
            search: Function call action search to update.
        """

        statement = (
            update(ActionSearch)
            .where(
                col(ActionSearch.tx_signer_key) == search.tx_signer_key,
                col(ActionSearch.is_locked).is_(False),
            )
            .values(is_locked=True)
        )

        result: CursorResult = self._session.exec(statement)
        return result.rowcount == 1

    def unlock(self, search: ActionSearch) -> None:
        """
        Unlocks the function call action search.

        Args:
            search: Function call action search to update.
        """

        statement = (
            update(ActionSearch)
            .where(
                col(ActionSearch.tx_signer_key) == search.tx_signer_key,
            )
            .values(is_locked=False)
        )

        self._session.exec(statement)
        self._session.refresh(search)

    def get(self, tx_signer_key: str) -> ActionSearch | None:
        """
        Returns a function call action search by transaction signer key.

        Args:
            tx_signer_key: Transaction signer key.

        Returns:
            The function call action search or `None` if it does not exist.
        """
        return self._session.get(ActionSearch, tx_signer_key)

    def add(self, search: ActionSearch) -> None:
        """
        Adds a function call action search to the current database session.

        Args:
            search: Function call action search to add.
        """
        self._session.add(search)

    def safe_add(self, search: ActionSearch) -> ActionSearch:
        """
        Adds and flushes a function call action search within a savepoint.

        If an integrity conflict occurs, the savepoint is rolled back
        without rolling back the surrounding transaction.

        Args:
            search: Function call action search to add.

        Returns:
            The added function call action search.

        Raises:
            ActionSearchRepositoryError:
                If the function call action search could not be added.
        """
        try:
            with self._session.begin_nested():
                # savepoint
                self.add(search)
                self.flush()

            return search

        except IntegrityError:
            raise ActionSearchRepositoryError(
                f"Cannot add function call action search "
                f"for transaction signer key: {search.tx_signer_key}"
            )

    def update(
        self,
        search: ActionSearch,
        up_to_tx_block_height: int,
    ) -> None:
        """
        Updates the upper transaction block height of a function call action search.

        Args:
            search: Function call action search to update.
            up_to_tx_block_height: New inclusive upper transaction block height.
        """
        if not search.is_locked:
            raise ActionSearchRepositoryError(
                f"Function call action search is not locked "
                f"to update for transaction signer key: {search.tx_signer_key}"
            )
        
        if (
            search.up_to_tx_block_height is not None
            and up_to_tx_block_height < search.up_to_tx_block_height
        ):
            raise ActionSearchRepositoryError(
                f"`up_to_tx_block_height` must not decrease "
                f"for transaction signer key: {search.tx_signer_key}"
            )

        search.up_to_tx_block_height = up_to_tx_block_height
        self._session.add(search)

    def flush(self) -> None:
        """Flushes pending changes to the database."""
        self._session.flush()
