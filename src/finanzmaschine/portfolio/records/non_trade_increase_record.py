from dataclasses import dataclass
from typing import TypeVar

from finanzmaschine.portfolio.assets import BaseAsset
from finanzmaschine.portfolio.operation_types.non_trade_increase_type import NonTradeIncreaseRecord
from finanzmaschine.portfolio.records.base_record import Direction
from finanzmaschine.portfolio.records.priced_record import PricedRecord

A = TypeVar("A", bound=BaseAsset)
O = TypeVar("O", bound="NonTradeIncreaseRecord")


@dataclass(frozen=True)
class NonTradeIncreaseRecord(PricedRecord[A, O]):

    def __post_init__(self):
        super().__post_init__()

        if self.direction is not None and self.direction != Direction.IN:
            raise ValueError(f"Direction of non-trade increase records must be always {Direction.IN!r}")
