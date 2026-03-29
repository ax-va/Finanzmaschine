from dataclasses import dataclass

from finanzmaschine.portfolio.assets.base_asset import BaseAsset
from finanzmaschine.portfolio.records.base_record import BaseRecord, Direction


@dataclass(frozen=True)
class PricedRecord[A: BaseAsset](BaseRecord):
    quote_asset: A
    price: float
    fee: float

    def __post_init__(self) -> None:
        super().__post_init__()

        if not (self.price > 0):
            raise ValueError("Price must be positive")

        if not (self.fee >= 0):
            raise ValueError("Fee must be not negative")

    @property
    def gross_value(self) -> float:
        return self.quantity * self.price

    @property
    def quote_asset_flow(self) -> float:
        if self.direction == Direction.IN:
            return -(self.gross_value + self.fee)
        elif self.direction == Direction.OUT:
            return self.gross_value - self.fee
        else:
            raise ValueError("Direction is not specified")
