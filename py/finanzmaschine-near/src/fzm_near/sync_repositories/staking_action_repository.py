from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from fzm_near.orm.staking_action import StakingAction


class StakingActionRepository:
    """Provides synchronous database operations for NEAR staking actions."""

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
        receipt_key: str,
        action_index: int,
    ) -> StakingAction | None:
        """
        Returns a staking action by its composite primary key.

        Args:
            receipt_key: Receipt identifier.
            action_index: Index of the action within the receipt.

        Returns:
            The staking action or `None` if it does not exist.
        """
        return self._session.get(
            StakingAction,
            (receipt_key, action_index),
        )

    def add(self, action: StakingAction) -> None:
        """
        Adds a staking action to the current database session.

        Args:
            action: Staking action to add.
        """
        self._session.add(action)

    def flush(self) -> None:
        """Flushes pending changes to the database."""
        self._session.flush()

    def safe_add(self, action: StakingAction) -> bool:
        """
        Adds and flushes a staking action within a savepoint.

        If an integrity conflict occurs,
        the savepoint is rolled back
        without rolling back the surrounding transaction.

        Args:
            action: Staking action to add.

        Returns:
            `True` if the staking action was successfully flushed, otherwise `False`.
        """
        try:
            with self._session.begin_nested():
                # savepoint
                self.add(action)
                self.flush()

            return True

        except IntegrityError:
            return False