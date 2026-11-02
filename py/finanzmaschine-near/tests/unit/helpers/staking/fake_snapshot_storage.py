from fzm_near.helpers import constants as const
from fzm_near.orm.staking.balance import Balance


class FakeSnapshotStorage:
    def __init__(self) -> None:
        self.balances: dict[int, Balance] = {}
        self.saved: dict[tuple[int, int], dict[int, Balance]] = {}

    def add(
        self,
        balance: Balance,
    ) -> None:
        if balance.block_height in self.balances:
            raise ValueError(
                f"Snapshot already exists for {const.BLOCK_HEIGHT}={balance.block_height}"
            )

        self.balances[balance.block_height] = balance

    def get(
        self,
        block_height: int,
    ) -> Balance | None:
        return self.balances.get(block_height)

    def clear(self) -> None:
        self.balances.clear()

    def save(
        self,
        from_block_height: int,
        up_to_block_height: int,
    ) -> None:
        if up_to_block_height < from_block_height:
            raise ValueError(
                "`up_to_block_height` must be greater than "
                "or equal to `from_block_height`"
            )

        self.saved[
            (from_block_height, up_to_block_height)
        ] = self.balances.copy()
