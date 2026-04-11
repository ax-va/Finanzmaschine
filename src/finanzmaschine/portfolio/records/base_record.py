from abc import ABC
from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self, Any

from finanzmaschine.portfolio.operation_types.base_operation_type import BaseOperationType


class Direction(StrEnum):
    IN = "IN"
    OUT = "OUT"


@dataclass(frozen=True)
class BaseRecord[T: BaseOperationType](ABC):
    quantity: Decimal
    datetime: datetime
    direction: Direction
    operation_type: T

    def __post_init__(self) -> None:
        if not (self.quantity > Decimal("0")):
            raise ValueError("Quantity must be positive")

    def copy(self, **kwargs: Any) -> Self:
        return replace(self,**kwargs)
