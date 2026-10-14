import logging

import httpx
from sqlmodel import Session

from fzm_keying import KeyMapping

from fzm_near.orm.staking_action import StakingAction
from fzm_near.orm.staking_action_search import StakingActionSearch
from fzm_near.staking.factories import create_staking_actions
from fzm_near.sync_clients.txs_client import TxsClient
from fzm_near.sync_clients.fetchers import fetch_final_block_height, fetch_raw_txs
from fzm_near.sync_repositories.staking_action_repository import StakingActionRepository
from fzm_near.sync_repositories.staking_action_search_repository import StakingActionSearchRepository

logger = logging.getLogger(__name__)


class StakingActionService:
    def __init__(
        self,
        session: Session,
        key_mapping: KeyMapping,
    ) -> None:
        self._session: Session = session
        self._search_repo = StakingActionSearchRepository(session)
        self._action_repo = StakingActionRepository(session)
        self._key_mapping = key_mapping


    def get_actions(
        self,
        account_key: str,
        pool_key: str | None = None,
        from_tx_block_height: int | None = None,
        up_to_tx_block_height: int | None = None,
        from_receipt_block_height: int | None = None,
        up_to_receipt_block_height: int | None = None,
    ) -> list[StakingAction]:

        up_to_block_height: int = fetch_final_block_height()

        self.sync_actions(
            account_key=account_key,
            up_to_block_height=up_to_block_height,
        )

        actions: list[StakingAction] = self._action_repo.get(
            account_key=account_key,
            pool_key=pool_key,
            from_tx_block_height=from_tx_block_height,
            up_to_tx_block_height=up_to_tx_block_height,
            from_receipt_block_height=from_receipt_block_height,
            up_to_receipt_block_height=up_to_receipt_block_height,
        )

        return actions

    def sync_actions(
        self,
        account_key: str,
        up_to_block_height: int,
    ) -> None:
        actions: list[StakingAction]
        block_height: int | None
        search: StakingActionSearch | None = None
        locked = False

        try:
            search = self._search_repo.get(account_key)

            if search is None:
                # Create the first action search
                search: StakingActionSearch = StakingActionSearch(
                    account_key=account_key,
                )
                self._search_repo.safe_add(search)
                self._session.commit()

            self._search_repo.lock(search)
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
                    account_key=account_key,
                    from_tx_block_height=(
                        block_height + 1
                        if block_height is not None
                        else None
                    ),
                    up_to_tx_block_height=up_to_block_height,
                )
            )

            for action in actions:
                self._action_repo.safe_add(action)

            self._search_repo.update(
                search=search,
                up_to_tx_block_height=up_to_block_height,
            )

            self._session.commit()

        except Exception:
            self._session.rollback()
            logger.exception("Failed to synchronize staking actions")
            raise

        finally:
            if locked and search is not None:
                try:
                    self._search_repo.unlock(search)
                    self._session.commit()
                except Exception:
                    self._session.rollback()
                    logger.exception("Failed to synchronize staking actions")
                    raise

    def fetch_actions(
        self,
        account_key: str,
        from_tx_block_height: int | None = None,
        up_to_tx_block_height: int | None = None,
    ) -> list[StakingAction]:

        raw_txs: list[dict] = fetch_raw_txs(
           account_id=self._key_mapping.get_value(account_key),
           up_to_tx_block_height=up_to_tx_block_height,
           from_tx_block_height=from_tx_block_height,
        )

        actions: list[StakingAction] = create_staking_actions(
            raw_txs=raw_txs,
            key_mapping=self._key_mapping,
        )

        return actions
