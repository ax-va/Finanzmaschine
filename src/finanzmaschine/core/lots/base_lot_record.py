from dataclasses import dataclass
from datetime import datetime

from finanzmaschine.core.assets.asset import Asset


@dataclass(frozen=True)
class BaseLotRecord:
    quantity: float
    price: float
    quote_asset: Asset
    fee: float
    fee_asset: Asset
    dt: datetime

    def __post_init__(self) -> None:
        if not (self.quantity > 0):
            raise ValueError("`quantity` must be positive")

        if not (self.price > 0):
            raise ValueError("`price` must be positive")

        if not (self.fee >= 0):
            raise ValueError("`fee` must be not negative")
