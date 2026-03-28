from dataclasses import dataclass, asdict
from datetime import datetime
from enum import StrEnum
from typing import Self, Any

from finanzmaschine.core.assets.base_asset import BaseAsset


class Direction(StrEnum):
    IN = "IN"
    OUT = "OUT"


@dataclass(frozen=True)
class BaseRecord[A: "BaseAsset"]:
    direction: Direction | None
    quantity: float
    quote_asset: A
    price: float
    fee: float
    dt: datetime

    def __post_init__(self) -> None:
        if not (self.quantity > 0):
            raise ValueError("Quantity must be positive")

        if not (self.price > 0):
            raise ValueError("Price must be positive")

        if not (self.fee >= 0):
            raise ValueError("Fee must be not negative")

    @property
    def gross_value(self) -> float:
        return self.quantity * self.price

    @property
    def cash_flow(self) -> float:
        if self.direction == Direction.IN:
            return -(self.gross_value + self.fee)
        elif self.direction == Direction.OUT:
            return self.gross_value - self.fee
        else:
            raise ValueError("Direction is not specified")

    @property
    def cost_basis(self) -> float:
        if self.direction == Direction.IN:
            return (self.gross_value + self.fee) / self.quantity
        else:
            raise ValueError(f"{self.direction!r} record has no cost basis")

    def copy(self, **kwargs: Any) -> Self:
        attr_dict = asdict(self)
        for k in kwargs:
            attr_dict.pop(k)
        return type(self)(**kwargs, **attr_dict)
