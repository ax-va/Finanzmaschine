from typing import Protocol

from fzm_near.orm.staking.balance import Balance


class BalanceFetcher(Protocol):
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
