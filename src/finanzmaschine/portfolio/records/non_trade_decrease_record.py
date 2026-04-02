from dataclasses import dataclass
from typing import TypeVar

from finanzmaschine.portfolio.operation_types.non_trade_decrease_type import NonTradeDecreaseRecord
from finanzmaschine.portfolio.records.base_record import BaseRecord, Direction

O = TypeVar("O", bound="NonTradeDecreaseRecord")


@dataclass(frozen=True)
class NonTradeDecreaseRecord(BaseRecord[O]):

    def __post_init__(self):
        super().__post_init__()

        if self.direction is not None and self.direction != Direction.OUT:
            raise ValueError(f"Direction of non-trade decrease records must be always {Direction.OUT!r}")
