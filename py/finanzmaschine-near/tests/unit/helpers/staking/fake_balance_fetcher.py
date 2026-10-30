from collections.abc import Callable

from fzm_near.orm.staking.balance import Balance
from fzm_near.sync_clients.errors import BlockHeightNotFoundError


class FakeBalanceFetcher:
    def __init__(
        self,
        get_balance: Callable[[int], Balance],
        is_missing_block: Callable[[int], bool] | None = None,
    ) -> None:
        self._get_balance = get_balance
        self._is_missing_block = is_missing_block or (lambda _: False)
        self.requested_heights: list[int] = []

    def fetch_balance(
        self,
        account_id: str,
        pool_id: str,
        block_height: int,
    ) -> Balance:
        self.requested_heights.append(block_height)

        if self._is_missing_block(block_height):
            raise BlockHeightNotFoundError(
                f"Block height not found: {block_height}"
            )

        return self._get_balance(block_height)