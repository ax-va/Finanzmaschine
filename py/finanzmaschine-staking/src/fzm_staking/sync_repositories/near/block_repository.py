from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from fzm_crypto.orm.near.block import Block


class BlockRepository:
    """Provides synchronous database operations for NEAR blocks."""

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

    def get(self, block_height: int) -> Block | None:
        """
        Returns a block by its height.

        Args:
            block_height: Block height.

        Returns:
            The block or `None` if it doesn't exist.
        """
        return self._session.get(Block, block_height)

    def add(self, block: Block) -> None:
        """
        Adds a block to the current database session.

        Args:
            block: Block to add.
        """
        self._session.add(block)

    def flush(self) -> None:
        """Flushes pending changes to the database."""
        self._session.flush()

    def safe_add(self, block: Block) -> bool:
        """
        Adds and flushes a block within a savepoint.

        If an integrity conflict occurs,
        the savepoint is rolled back
        without rolling back the surrounding transaction.

        Args:
            block: Block to add.

        Returns:
            `True` if the block was successfully flushed, otherwise `False`.
        """
        try:
            with self._session.begin_nested():
                # savepoint
                self.add(block)
                self.flush()

            return True

        except IntegrityError:
            return False
