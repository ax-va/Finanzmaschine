from dataclasses import dataclass

from finanzmaschine.portfolio.operation_types.non_trade_decrease_type import NonTradeDecreaseType
from finanzmaschine.portfolio.records.base_record import BaseRecord, Direction


@dataclass(frozen=True)
class NonTradeDecreaseRecord[T: NonTradeDecreaseType](BaseRecord[T]):

    def __post_init__(self):
        super().__post_init__()

        if self.direction is not None and self.direction != Direction.OUT:
            raise ValueError(f"Direction of non-trade decrease records must always be {Direction.OUT!r}")
