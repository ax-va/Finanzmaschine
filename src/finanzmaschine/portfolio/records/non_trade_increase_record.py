from dataclasses import dataclass

from finanzmaschine.portfolio.assets.asset import Asset
from finanzmaschine.portfolio.operation_types.non_trade_increase_type import NonTradeIncreaseType
from finanzmaschine.portfolio.records.base_record import Direction
from finanzmaschine.portfolio.records.priced_record import PricedRecord


@dataclass(frozen=True, eq=False)
class NonTradeIncreaseRecord[Q: Asset, T: NonTradeIncreaseType](PricedRecord[Q, T]):

    def __post_init__(self):
        super().__post_init__()

        if self.direction is not None and self.direction != Direction.IN:
            raise ValueError(f"Direction of non-trade increase records must always be {Direction.IN!r}")
