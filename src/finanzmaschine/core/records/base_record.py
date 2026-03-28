from dataclasses import dataclass, asdict
from datetime import datetime
from enum import StrEnum
from typing import Self, Any

from finanzmaschine.core.assets.base_asset import BaseAsset


class RecordDirection(StrEnum):
    IN = "IN"
    OUT = "OUT"


@dataclass(frozen=True)
class BaseRecord[A: "BaseAsset"]:
    quantity: float
    quote_asset: A
    price: float
    fee: float
    dt: datetime
    direction: RecordDirection | None = None

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
