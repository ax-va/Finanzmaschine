from typing import Protocol

from fzm_near.orm.staking.balance import Balance


class BalanceFetcherProtocol(Protocol):
    """
    Defines the interface for fetching staking balances
    at specified block heights.
    """
    def fetch_balance(
        self,
        account_id: str,
        pool_id: str,
        block_height: int,
    ) -> Balance:
        """
        Fetches a staking total balance at the specified block height.

        Raises:
            BlockHeightNotFoundError:
                If the requested block height does not exist.
        """
        ...


class SnapshotStorageProtocol(Protocol):
    """
    Defines the interface for accumulating, retrieving, clearing,
    and saving staking balance snapshots.
    """
    def add(self, balance: Balance) -> None:
        ...

    def clear(self) -> None:
        ...

    def get(self, block_height: int) -> Balance | None:
        ...

    def save(
        self,
        from_block_height: int,
        up_to_block_height: int,
    ) -> None:
        ...
