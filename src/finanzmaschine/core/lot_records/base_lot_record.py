from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Self, Any

from finanzmaschine.core.assets.base_asset import BaseAsset


@dataclass(frozen=True)
class BaseLotRecord[A: "BaseAsset"]:
    quantity: float
    quote_asset: A
    price: float
    fee: float
    dt: datetime

    def __post_init__(self) -> None:
        if not (self.quantity > 0):
            raise ValueError("`quantity` must be positive")

        if not (self.price > 0):
            raise ValueError("`price` must be positive")

        if not (self.fee >= 0):
            raise ValueError("`fee` must be not negative")


    def copy(self, **kwargs: Any) -> Self:
        attr_dict = asdict(self)
        for k in kwargs:
            attr_dict.pop(k)
        return type(self)(**kwargs, **attr_dict)
