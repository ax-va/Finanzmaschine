from abc import ABC
from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from typing import Self, Any, Tuple

from finanzmaschine_core.portfolio.operations.base_operation_enum import BaseOperationEnum


@dataclass(frozen=True, eq=False, kw_only=True)
class BaseRecord[OP: BaseOperationEnum](ABC):
    """
    Base class for all internal lot records.
    Not to be confused with a broker transaction.
    """
    quantity: Decimal
    datetime: datetime
    operation: OP

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
