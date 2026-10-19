from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, col

from fzm_near.orm.function_call.action import Action
from fzm_near.sync_repositories.function_call.action_repository_errors import ActionRepositoryError


class ActionRepository:
    """Provides synchronous database operations for NEAR function call actions."""

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
    ) -> Action | None:
        """
        Returns a function call action by its composite primary key.

        Args:
            receipt_key: Receipt identifier.
            action_index: Index of the action within the receipt.

        Returns:
            The function call action or `None` if it does not exist.
        """
        return self._session.get(
            Action,
            (receipt_key, action_index),
        )

    def get(
        self,
        tx_signer_key: str,
        receipt_predecessor_key: str | None = None,
        receiver_key: str | None = None,
        tx_key: str | None = None,
        from_tx_block_height: int | None = None,
        up_to_tx_block_height: int | None = None,
        from_receipt_block_height: int | None = None,
        up_to_receipt_block_height: int | None = None,
        from_exec_outcome_block_height: int | None = None,
        up_to_exec_outcome_block_height: int | None = None,
    ) -> list[Action]:
        """
        Returns function call actions for a transaction signer key,
        optionally filtered by keys of receipt predecessor ID, receiver ID and transaction hash,
        as well as block heights of transaction, receipt and execution outcome.

        Args:
            tx_signer_key: Transaction signer key. In the case of staking, account key.
            receipt_predecessor_key: Optional receipt predecessor key. In the case of staking account key.
            receiver_key: Optional receiver key. In the case of staking, pool key.
            tx_key: Optional transaction key mapping the transaction hash.
            from_tx_block_height: Optional inclusive lower transaction block height.
            up_to_tx_block_height: Optional inclusive upper transaction block height.
            from_receipt_block_height: Optional inclusive lower receipt block height.
            up_to_receipt_block_height: Optional inclusive upper receipt block height.
            from_exec_outcome_block_height: Optional inclusive upper execution outcome block height.
            up_to_exec_outcome_block_height: Optional inclusive lower execution outcome block height.

        Returns:
            Matching function call actions
            ordered by execution outcome block height,
            execution outcome index, and action index.
        """
        statement = select(Action).where(
            Action.tx_signer_key == tx_signer_key
        )

        if receipt_predecessor_key is not None:
            statement = statement.where(
                Action.receipt_predecessor_key == receipt_predecessor_key
            )

        if receiver_key is not None:
            statement = statement.where(
                Action.receiver_key == receiver_key
            )

        if tx_key is not None:
            statement = statement.where(
                Action.tx_key == tx_key
            )

        if from_tx_block_height is not None:
            statement = statement.where(
                from_tx_block_height <= Action.tx_block_height
            )

        if up_to_tx_block_height is not None:
            statement = statement.where(
                Action.tx_block_height <= up_to_tx_block_height
            )

        if from_receipt_block_height is not None:
            statement = statement.where(
                from_receipt_block_height <= Action.receipt_block_height
            )

        if up_to_receipt_block_height is not None:
            statement = statement.where(
                Action.receipt_block_height <= up_to_receipt_block_height
            )

        if from_exec_outcome_block_height is not None:
            statement = statement.where(
                from_exec_outcome_block_height <= Action.exec_outcome_block_height
            )

        if up_to_exec_outcome_block_height is not None:
            statement = statement.where(
                Action.exec_outcome_block_height <= up_to_exec_outcome_block_height
            )

        statement = statement.order_by(
            col(Action.exec_outcome_block_height),
            col(Action.exec_outcome_index),
            col(Action.action_index),
        )

        return list(self._session.exec(statement).all())

    def add(self, action: Action) -> None:
        """
        Adds a function call action to the current database session.

        Args:
            action: Faunction call action to add.
        """
        self._session.add(action)

    def flush(self) -> None:
        """Flushes pending changes to the database."""
        self._session.flush()

    def safe_add(self, action: Action) -> None:
        """
        Adds a function call action within a savepoint.

        Ignores an integrity conflict
        if an action with the same primary key already exists.
        Raises an error otherwise.

        Args:
            action: Function call action to add.
        """
        try:
            with self._session.begin_nested():
                # savepoint
                self.add(action)
                self.flush()

        except IntegrityError as e:
            # The savepoint transaction is rolled back
            action_: Action | None = self.get_by_pk(
                receipt_key=action.receipt_key,
                action_index=action.action_index,
            )

            if action_ is not None:
                # The action failed to add
                # already exists in the database.
                return

            raise ActionRepositoryError(
                f"Cannot add function call action "
                f"for transaction signer key: {action.tx_signer_key}"
            ) from e
