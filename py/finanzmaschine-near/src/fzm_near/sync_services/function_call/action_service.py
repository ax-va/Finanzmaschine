import logging

import polars as pl
from sqlmodel import Session

from fzm_keying import KeyMappingProtocol

from fzm_near.orm.function_call.action import Action
from fzm_near.orm.function_call.action_search import ActionSearch
from fzm_near.helpers import constants as const
from fzm_near.helpers.function_call.factories import create_actions
from fzm_near.helpers.staking.df_schemas import ACTION_SCHEMA as STAKING_ACTION_SCHEMA
from fzm_near.helpers.staking.enums import MethodNameEnum
from fzm_near.helpers.staking.extractors import extract_operation_yocto_str
from fzm_near.sync_clients.fastnear_fetchers import (
    fetch_final_block_height,
    fetch_txs,
)
from fzm_near.sync_repositories.function_call.action_repository import ActionRepository
from fzm_near.sync_repositories.function_call.action_search_repository import ActionSearchRepository
from fzm_near.sync_services.function_call.receiver_service import ReceiverService

logger = logging.getLogger(__name__)


class ActionService:
    """Fetches, synchronizes, and retrieves NEAR function call actions."""

    def __init__(
        self,
        session: Session,
        key_mapping: KeyMappingProtocol,
    ) -> None:
        """
        Args:
            session: Database session.
            key_mapping: Protocol for mapping between keys and NEAR identifiers.
        """

        self._session: Session = session
        self._action_repository = ActionRepository(session)
        self._search_repository = ActionSearchRepository(session)
        self._key_mapping: KeyMappingProtocol = key_mapping

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

        final_block_height: int = fetch_final_block_height()

        self.sync_actions(
            tx_signer_key=tx_signer_key,
            up_to_tx_block_height=final_block_height,
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
        up_to_tx_block_height: int | None = None,
    ) -> int | None:
        """
        Synchronizes a signer's function call actions up to a block height.

        Uses a repository lock to prevent concurrent synchronization.
        Fetches and stores actions not yet synchronized,
        updates the synchronization progress, and releases the lock afterward.
        A successfully processed range may contain no function call actions.

        Args:
            tx_signer_key: Key identifying the transaction signer.
            up_to_tx_block_height: Optional transaction block height through which to synchronize.

        Returns:
            The transaction block height through which function call actions have been
            successfully synchronized, including when no new synchronization was necessary.
            `None` if the search lock could not be acquired.

        Raises:
            Exception:
                If synchronization or unlocking fails.
        """

        if up_to_tx_block_height is None:
            up_to_tx_block_height: int = fetch_final_block_height()

        search: ActionSearch | None = None
        is_locked = False

        try:
            search = self._search_repository.get(tx_signer_key)

            if search is None:
                # Create the first function call search
                search: ActionSearch = ActionSearch(
                    tx_signer_key=tx_signer_key,
                )
                self._search_repository.safe_add(search)
                self._session.commit()

            is_locked = self._search_repository.lock(search)

            if not is_locked:
                self._session.rollback()
                return None

            # Read the search progress after acquiring the lock
            self._session.refresh(search)
            # Determine up to which block height
            # the function call search was already processed.
            previous_block_height: int | None = search.up_to_tx_block_height

            self._session.commit()

            if (
                previous_block_height is not None
                and previous_block_height >= up_to_tx_block_height
            ):
                # Function call actions were already synchronized
                return previous_block_height

            actions: list[Action] = (
                self.fetch_actions(
                    tx_signer_key=tx_signer_key,
                    from_tx_block_height=(
                        previous_block_height + 1
                        if previous_block_height is not None
                        else None
                    ),
                    up_to_tx_block_height=up_to_tx_block_height,
                )
            )

            for action in actions:
                self._action_repository.safe_add(action)

            # Update up to which block height
            # the function call search is processed now.
            self._search_repository.update(
                search=search,
                up_to_tx_block_height=up_to_tx_block_height,
            )

            self._session.commit()

            return up_to_tx_block_height

        except Exception:
            self._session.rollback()

            logger.exception(
                f"Failed to synchronize function calls "
                f"for `tx_signer_key` {tx_signer_key}"
            )

            raise

        finally:
            if is_locked and search is not None:
                try:
                    self._search_repository.unlock(search)
                    self._session.commit()

                except Exception:
                    self._session.rollback()

                    logger.exception(
                        f"Failed to unlock the function call search "
                        f"when synchronizing function calls "
                        f"for `tx_signer_key` {tx_signer_key}"
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

        txs: dict[str, list[dict]] = fetch_txs(
           account_id=self._key_mapping.get_value(tx_signer_key),
           up_to_tx_block_height=up_to_tx_block_height,
           from_tx_block_height=from_tx_block_height,
        )

        actions: list[Action] = create_actions(
            txs=txs,
            key_mapping=self._key_mapping,
        )

        return actions

    def create_df_staking_actions(
        self,
        actions: list[Action],
    ) -> pl.DataFrame:
        """
        Filters function call actions and converts them into staking actions.

        Preserves the original action order and checks each unique receiver only once.

        Args:
            actions: Function call actions to process.

        Returns:
            Dataframe with staking actions for verified staking pool receivers.
        """

        receiver_service = ReceiverService(
            session=self._session,
            key_mapping=self._key_mapping,
        )

        receiver_results: dict[str, bool] = {}
        rows: list[dict] = []

        for action in actions:
            try:
                method_name = MethodNameEnum(action.method_name)
            except ValueError:
                continue

            receiver_key = action.receiver_key

            if receiver_key not in receiver_results:
                receiver_results[receiver_key] = (
                    receiver_service.is_staking_pool(receiver_key)
                )

            if not receiver_results[receiver_key]:
                continue

            rows.append(
                {
                    const.RECEIPT_KEY: action.receipt_key,
                    const.ACTION_INDEX: action.action_index,
                    const.ACCOUNT_KEY: action.tx_signer_key,
                    const.POOL_KEY: action.receiver_key,
                    const.EXEC_OUTCOME_BLOCK_HEIGHT: action.exec_outcome_block_height,
                    const.EXEC_OUTCOME_INDEX: action.exec_outcome_index,
                    const.METHOD_NAME: method_name.value,
                    const.OPERATION_YOCTO_STR: extract_operation_yocto_str(action=action),
                }
            )

        return pl.DataFrame(
            data=rows,
            schema=STAKING_ACTION_SCHEMA,
        )
