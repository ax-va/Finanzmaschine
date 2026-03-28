from dataclasses import dataclass
from enum import StrEnum

from finanzmaschine.core.records.base_record import BaseRecord, Direction


class Reason(StrEnum):
    TRANSFER = "TRANSFER"


@dataclass(frozen=True)
class NonPricedRecord(BaseRecord):
    reason: Reason | None

    def __post_init__(self):
        super().__post_init__()

        if self.direction is not None and self.direction != Direction.OUT:
            raise ValueError(f"Direction of the non-priced record must be {Direction.OUT!r}")
