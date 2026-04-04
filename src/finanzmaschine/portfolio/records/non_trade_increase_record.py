from dataclasses import dataclass
from typing import TypeVar

from finanzmaschine.portfolio.assets.asset import Asset
from finanzmaschine.portfolio.operation_types.non_trade_increase_type import NonTradeIncreaseType
from finanzmaschine.portfolio.records.base_record import Direction
from finanzmaschine.portfolio.records.priced_record import PricedRecord

Q = TypeVar("Q", bound=Asset)
O = TypeVar("O", bound=NonTradeIncreaseType)


@dataclass(frozen=True)
class NonTradeIncreaseRecord(PricedRecord[Q, O]):

    def __post_init__(self):
        super().__post_init__()

        if self.direction is not None and self.direction != Direction.IN:
            raise ValueError(f"Direction of non-trade increase records must always be {Direction.IN!r}")
