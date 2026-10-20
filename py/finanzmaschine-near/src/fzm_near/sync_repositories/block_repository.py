from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from fzm_near.orm.block import Block
from fzm_near.sync_repositories.block_repository_errors import BlockRepositoryError


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

    def safe_add(self, block: Block) -> Block:
        """
        Adds and flushes a block within a savepoint.

        If an integrity conflict occurs,
        the savepoint is rolled back
        without rolling back the surrounding transaction.

        Args:
            block: Block to add.

        Returns:
            The added block or the existing block.

        Raises:
            BlockRepositoryError:
                If the block could not be added.
        """
        try:
            with self._session.begin_nested():
                # savepoint
                self.add(block)
                self.flush()

            return block

        except IntegrityError as e:
            # The savepoint transaction is rolled back
            block_: Block | None = self.get(
                block_height=block.block_height,
            )

            if block_ is not None:
                # The block failed to add
                # already exists in the database.
                return block_

            raise BlockRepositoryError(
                f"Cannot add block at block height: {block.block_height}"
            ) from e
