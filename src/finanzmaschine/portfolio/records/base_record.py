from abc import ABC
from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from typing import Self, Any
from uuid import UUID

from finanzmaschine.portfolio.operation_types.base_operation_type import BaseOperationType


class Direction(StrEnum):
    IN = "IN"
    OUT = "OUT"


@dataclass(frozen=True)
class BaseRecord[O: BaseOperationType](ABC):
    id: UUID
    quantity: float
    datetime: datetime
    direction: Direction
    operation_type: O
    split_from_id: UUID | None

    def __post_init__(self) -> None:
        if not (self.quantity > 0):
            raise ValueError("Quantity must be positive")

    def copy(self, **kwargs: Any) -> Self:
        return replace(self,**kwargs)
