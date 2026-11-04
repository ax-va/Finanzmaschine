from fzm_near.helpers import constants as const
from fzm_near.orm.staking.balance import Balance


class FakeSnapshotStorage:
    def __init__(self) -> None:
        self.balances: list[Balance] = []
        self.saved: dict[tuple[int, int], list[Balance]] = {}

    @property
    def saved_balances(self) -> list[Balance]:
        balances: list[Balance] = []
        for values in self.saved.values():
            balances += values
        return balances

    def add(
        self,
        balance: Balance,
    ) -> None:
        if self.get(balance.block_height) is not None:
            raise ValueError(
                f"Snapshot already exists for {const.BLOCK_HEIGHT}={balance.block_height}"
            )
        self.balances.append(balance)

    def get(
        self,
        block_height: int,
    ) -> Balance | None:
        for balance in self.balances:
            if balance.block_height == block_height:
                return balance
        return None

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
