from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from finanzmaschine.catalog.asset_enum import Asset


@dataclass(frozen=True)
class BaseLotRecord:
    quantity: float
    price: Decimal
    quote_asset: Asset
    fee: Decimal
    fee_asset: Asset
    dt: datetime

    def __post_init__(self) -> None:
        if not (self.quantity > 0):
            raise ValueError("`quantity` must be positive")

        if not (self.price > 0):
            raise ValueError("`price` must be positive")

        if not (self.fee >= 0):
            raise ValueError("`fee` must be not negative")
