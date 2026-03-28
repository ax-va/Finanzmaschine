from dataclasses import dataclass, asdict
from datetime import datetime
from enum import StrEnum
from typing import Self, Any


class Direction(StrEnum):
    IN = "IN"
    OUT = "OUT"


@dataclass(frozen=True)
class BaseRecord:
    direction: Direction | None
    quantity: float
    dt: datetime

    def __post_init__(self) -> None:
        if not (self.quantity > 0):
            raise ValueError("Quantity must be positive")

    def copy(self, **kwargs: Any) -> Self:
        attr_dict = asdict(self)
        for k in kwargs:
            attr_dict.pop(k)
        return type(self)(**kwargs, **attr_dict)
