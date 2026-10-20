from sqlmodel import Session

from fzm_keying import KeyMapping
from fzm_near.orm.receiver import Receiver
from fzm_near.sync_clients.fetchers import fetch_final_block_height, is_staking_pool_whitelisted
from fzm_near.sync_repositories.receiver_repository import ReceiverRepository


class ReceiverService:
    """Provides synchronous database operations for NEAR receivers."""

    def __init__(
        self,
        session: Session,
        key_mapping: KeyMapping,
    ) -> None:
        """
        Args:
            session: Database session.
            key_mapping: Mapping between receiver keys and receiver IDs.
        """

        self._session: Session = session
        self._repository = ReceiverRepository(session)
        self._key_mapping = key_mapping

    def is_staking_pool(
        self,
        receiver_key: str,
        block_height: int | None = None,
    ) -> bool:
        """
        Check whether a receiver is a staking pool, caching the result.

        Returns the stored classification if available.
        Otherwise, queries the staking pool whitelist at the specified block height
        or the latest final block height and stores the result for future lookups.

        Args:
            receiver_key: Unique key identifying the receiver.
            block_height:
                Block height for the whitelist query.
                Defaults to the latest final block height.

        Returns:
            `True` if the receiver is classified as a staking pool,
            `False` otherwise.
        """

        receiver: Receiver | None = self._repository.get(receiver_key)
        if receiver is not None:
            return receiver.is_staking_pool

        if block_height is None:
            block_height: int = fetch_final_block_height()

        is_staking_pool: bool = is_staking_pool_whitelisted(
            pool_id=self._key_mapping.get_value(receiver_key),
            block_height=block_height,
        )

        receiver: Receiver = self._repository.safe_add(
            Receiver(
                receiver_key=receiver_key,
                is_staking_pool=is_staking_pool,
            )
        )

        return receiver.is_staking_pool
