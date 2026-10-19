from sqlalchemy import update, CursorResult
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col

from fzm_near.orm.function_call.search import Search
from fzm_near.sync_repositories.function_call.search_repository_errors import SearchRepositoryError


class ActionSearchRepository:
    """Provides synchronous database operations for NEAR function call searches."""

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

    def lock(self, search: Search) -> None:
        """
        Atomically locks the function call search.

        Args:
            search: function call search to update.
        """

        statement =(
            update(Search)
            .where(
                col(Search.tx_signer_key) == search.tx_signer_key,
                col(Search.locked).is_(False)
            )
            .values(locked=True)
        )

        result: CursorResult = self._session.exec(statement)
        
        if result.rowcount != 1:
            raise SearchRepositoryError(
                f"Cannot lock function call search "
                f"for transaction signer key: {search.tx_signer_key}"
            )

        self._session.refresh(search)

    def unlock(self, search: Search) -> None:
        """
        Unlocks the function call search.

        Args:
            search: Function call search to update.
        """

        statement = (
            update(Search)
            .where(
                col(Search.tx_signer_key) == search.tx_signer_key,
            )
            .values(locked=False)
        )

        self._session.exec(statement)
        self._session.refresh(search)

    def get(self, tx_signer_key: str) -> Search | None:
        """
        Returns a function call search by transaction signer key.

        Args:
            tx_signer_key: Transaction signer key.

        Returns:
            The function call search or `None` if it does not exist.
        """
        return self._session.get(Search, tx_signer_key)

    def add(self, search: Search) -> None:
        """
        Adds a function call search to the current database session.

        Args:
            search: Function call search to add.
        """
        self._session.add(search)

    def safe_add(self, search: Search) -> None:
        """
        Adds and flushes a function call search within a savepoint.

        If an integrity conflict occurs, the savepoint is rolled back
        without rolling back the surrounding transaction.

        Args:
            search: Function call search to add.
        """
        try:
            with self._session.begin_nested():
                # savepoint
                self.add(search)
                self.flush()

        except IntegrityError:
            raise SearchRepositoryError(
                f"Cannot add function call search "
                f"for transaction signer key: {search.tx_signer_key}"
            )

    def update(
        self,
        search: Search,
        up_to_tx_block_height: int,
    ) -> None:
        """
        Updates the upper transaction block height of a function call search.

        Args:
            search: Function call search to update.
            up_to_tx_block_height: New inclusive upper transaction block height.
        """
        if not search.locked:
            raise SearchRepositoryError(
                f"Function call search is not locked "
                f"to update for transaction signer key: {search.tx_signer_key}"
            )
        
        if (
            search.up_to_tx_block_height is not None
            and up_to_tx_block_height < search.up_to_tx_block_height
        ):
            raise SearchRepositoryError(
                f"`up_to_tx_block_height` must not decrease "
                f"for transaction signer key: {search.tx_signer_key}"
            )

        search.up_to_tx_block_height = up_to_tx_block_height
        self._session.add(search)

    def flush(self) -> None:
        """Flushes pending changes to the database."""
        self._session.flush()
