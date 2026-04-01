from dataclasses import dataclass, replace
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
        return replace(self,**kwargs)
