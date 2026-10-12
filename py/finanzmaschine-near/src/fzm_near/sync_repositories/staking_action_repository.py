from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, col

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

    def get_by_pk(
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

    def get(
        self,
        account_key: str,
        pool_key: str | None = None,
        from_tx_block_height: int | None = None,
        up_to_tx_block_height: int | None = None,
        from_receipt_block_height: int | None = None,
        up_to_receipt_block_height: int | None = None,
    ) -> list[StakingAction]:
        """
        Returns staking actions for an account, optionally filtered
        by pool, transaction block heights, and receipt block heights.

        Args:
            account_key: Account identifier.
            pool_key: Optional staking pool identifier.
            from_tx_block_height: Optional inclusive lower transaction block height.
            up_to_tx_block_height: Optional inclusive upper transaction block height.
            from_receipt_block_height: Optional inclusive lower receipt block height.
            up_to_receipt_block_height: Optional inclusive upper receipt block height.

        Returns:
            Matching staking actions ordered by transaction block height,
            receipt block height, receipt key, and action index.
        """
        statement = select(StakingAction).where(
            StakingAction.account_key == account_key
        )

        if pool_key is not None:
            statement = statement.where(
                StakingAction.pool_key == pool_key
            )

        if from_tx_block_height is not None:
            statement = statement.where(
                from_tx_block_height <= StakingAction.tx_block_height
            )

        if up_to_tx_block_height is not None:
            statement = statement.where(
                StakingAction.tx_block_height <= up_to_tx_block_height
            )

        if from_receipt_block_height is not None:
            statement = statement.where(
                from_receipt_block_height <= StakingAction.receipt_block_height
            )

        if up_to_receipt_block_height is not None:
            statement = statement.where(
                StakingAction.receipt_block_height <= up_to_receipt_block_height
            )

        statement = statement.order_by(
            col(StakingAction.tx_block_height),
            col(StakingAction.receipt_block_height),
            col(StakingAction.receipt_key),
            col(StakingAction.action_index),
        )

        return list(self._session.exec(statement).all())

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