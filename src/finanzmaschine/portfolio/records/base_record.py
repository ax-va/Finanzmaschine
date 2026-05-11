from abc import ABC
from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self, Any, Tuple

from finanzmaschine.portfolio.operation_types.base_operation_type import BaseOperationType


class Direction(StrEnum):
    IN = "IN"
    OUT = "OUT"


@dataclass(frozen=True, eq=False)
class BaseRecord[T: BaseOperationType](ABC):
    """
    Base class for all internal lot records.
    Not to be confused with a broker transaction.
    """
    quantity: Decimal
    datetime: datetime
    direction: Direction
    operation_type: T

    def __hash__(self) -> int:
        return id(self)

    def __post_init__(self) -> None:
        if not (self.quantity > Decimal("0")):
            raise ValueError("Quantity must be positive")

    def copy(self, **kwargs: Any) -> Self:
        return replace(self,**kwargs)

    def split(self, quantity: Decimal) -> Tuple[Self, Self]:
        return (
            self.copy(quantity=quantity),
            self.copy(quantity=self.quantity - quantity),
        )
