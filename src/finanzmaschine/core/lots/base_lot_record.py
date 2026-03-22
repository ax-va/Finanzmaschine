from dataclasses import dataclass, asdict
from datetime import datetime
from typing import TypeVar

from finanzmaschine.core.assets.asset import Asset

R = TypeVar("R", bound="BaseLotRecord")


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


    def clone_with_change(self, **kwargs) -> R:
        attr_dict = asdict(self)
        for k in kwargs:
            attr_dict.pop(k)

        return type(self)(**kwargs, **attr_dict)
