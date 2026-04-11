from dataclasses import dataclass
from decimal import Decimal
from typing import TypeVar, Generic

from finanzmaschine.portfolio.assets.asset import Asset
from finanzmaschine.portfolio.operation_types.priced_operation_type import PricedOperationType
from finanzmaschine.portfolio.records.base_record import BaseRecord, Direction
from finanzmaschine.utils.decimal_helper import round_to_quanta

Q = TypeVar("Q", bound=Asset)
O = TypeVar("O", bound=PricedOperationType)


@dataclass(frozen=True)
class PricedRecord(BaseRecord[O], Generic[Q, O]):
    quote_asset: Q
    price: Decimal
    fee: Decimal

    def __post_init__(self) -> None:
        super().__post_init__()

        if not (self.price > Decimal("0")):
            raise ValueError("Price must be positive")

        if not (self.fee >= Decimal("0")):
            raise ValueError("Fee must be not negative")

    @property
    def gross_value(self) -> Decimal:
        return self.quantity * self.price

    @property
    def quote_asset_flow(self) -> Decimal:
        if self.direction == Direction.IN:
            return -(self.gross_value + self.fee)
        elif self.direction == Direction.OUT:
            return self.gross_value - self.fee
        else:
            raise ValueError("Direction is not specified")
