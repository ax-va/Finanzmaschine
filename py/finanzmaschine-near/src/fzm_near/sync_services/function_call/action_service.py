import logging

from sqlmodel import Session

from fzm_keying import KeyMapping

from fzm_near.orm.function_call.action import Action
from fzm_near.orm.function_call.search import Search
from fzm_near.helpers.function_call.factories import create_actions
from fzm_near.sync_clients.fetchers import fetch_final_block_height, fetch_txs
from fzm_near.sync_repositories.function_call.action_repository import ActionRepository
from fzm_near.sync_repositories.function_call.search_repository import ActionSearchRepository

logger = logging.getLogger(__name__)


class ActionService:
    """Fetches, synchronizes, and retrieves NEAR function call actions."""

    def __init__(
        self,
        session: Session,
        key_mapping: KeyMapping,
    ) -> None:
        """
        Args:
            session: Database session.
            key_mapping: Mapping between keys and NEAR identifiers.
        """

        self._session: Session = session
        self._search_repository = ActionSearchRepository(session)
        self._action_repository = ActionRepository(session)
        self._key_mapping = key_mapping


    def get_actions(
        self,
        tx_signer_key: str,
        predecessor_key: str | None = None,
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
        Synchronizes and retrieves function call actions matching the filters.

        Synchronizes the signer's actions up to
        the latest final block before querying the database.

        Args:
            tx_signer_key: Key identifying the transaction signer.
            predecessor_key: Optional receipt predecessor key.
            receiver_key: Optional receipt receiver key.
            tx_key: Optional transaction key.
            from_tx_block_height: Minimum transaction block height.
            up_to_tx_block_height: Maximum transaction block height.
            from_receipt_block_height: Minimum receipt block height.
            up_to_receipt_block_height: Maximum receipt block height.
            from_exec_outcome_block_height:
                Minimum receipt execution outcome block height.
            up_to_exec_outcome_block_height:
                Maximum receipt execution outcome block height.

        Returns:
            List of function call actions matching the specified filters.
        """

        up_to_block_height: int = fetch_final_block_height()

        self.sync_actions(
            tx_signer_key=tx_signer_key,
            up_to_block_height=up_to_block_height,
        )

        actions: list[Action] = self._action_repository.get(
            tx_signer_key=tx_signer_key,
            predecessor_key=predecessor_key,
            receiver_key=receiver_key,
            tx_key=tx_key,
            from_tx_block_height=from_tx_block_height,
            up_to_tx_block_height=up_to_tx_block_height,
            from_receipt_block_height=from_receipt_block_height,
            up_to_receipt_block_height=up_to_receipt_block_height,
            from_exec_outcome_block_height=from_exec_outcome_block_height,
            up_to_exec_outcome_block_height=up_to_exec_outcome_block_height,
        )

        return actions

    def sync_actions(
        self,
        tx_signer_key: str,
        up_to_block_height: int,
    ) -> None:
        """
        Synchronizes a signer's function call actions up to a block height.

        Uses a repository lock to prevent concurrent synchronization.
        Fetches and stores actions not yet synchronized,
        updates the synchronization progress, and releases the lock afterward.

        Args:
            tx_signer_key: Key identifying the transaction signer.
            up_to_block_height: Block height through which to synchronize.
        """

        actions: list[Action]
        block_height: int | None
        search: Search | None = None
        locked = False

        try:
            search = self._search_repository.get(tx_signer_key)

            if search is None:
                # Create the first function call search
                search: Search = Search(
                    tx_signer_key=tx_signer_key,
                )
                self._search_repository.safe_add(search)
                self._session.commit()

            self._search_repository.lock(search)
            block_height = search.up_to_tx_block_height
            self._session.commit()
            locked = True

            if (
                block_height is not None
                and block_height >= up_to_block_height
            ):
                return

            actions = (
                self.fetch_actions(
                    tx_signer_key=tx_signer_key,
                    from_tx_block_height=(
                        block_height + 1
                        if block_height is not None
                        else None
                    ),
                    up_to_tx_block_height=up_to_block_height,
                )
            )

            for action in actions:
                self._action_repository.safe_add(action)

            self._search_repository.update(
                search=search,
                up_to_tx_block_height=up_to_block_height,
            )

            self._session.commit()

        except Exception:
            self._session.rollback()

            logger.exception(
                f"Failed to synchronize function calls "
                f"for `tx_signer_key`: {tx_signer_key}"
            )

            raise

        finally:
            if locked and search is not None:
                try:
                    self._search_repository.unlock(search)
                    self._session.commit()
                except Exception:
                    self._session.rollback()

                    logger.exception(
                        f"Failed to synchronize function calls "
                        f"for `tx_signer_key`: {tx_signer_key}"
                    )

                    raise

    def fetch_actions(
        self,
        tx_signer_key: str,
        from_tx_block_height: int | None = None,
        up_to_tx_block_height: int | None = None,
    ) -> list[Action]:
        """
        Fetches and creates function call actions for a transaction signer.

        Args:
            tx_signer_key: Key identifying the transaction signer.
            from_tx_block_height: Minimum transaction block height.
            up_to_tx_block_height: Maximum transaction block height.

        Returns:
            List of function call actions created from fetched transactions.
        """

        txs:  dict[str, list[dict]] = fetch_txs(
           account_id=self._key_mapping.get_value(tx_signer_key),
           up_to_tx_block_height=up_to_tx_block_height,
           from_tx_block_height=from_tx_block_height,
        )

        actions: list[Action] = create_actions(
            txs=txs,
            key_mapping=self._key_mapping,
        )

        return actions
