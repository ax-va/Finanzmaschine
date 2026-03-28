from dataclasses import dataclass
from enum import StrEnum

from finanzmaschine.core.records.base_record import BaseRecord, Direction


class Reason(StrEnum):
    TRANSFER_OUT = "TRANSFER_OUT"


@dataclass(frozen=True)
class NonPricedOutRecord(BaseRecord):
    reason: Reason | None

    def __post_init__(self):
        super().__post_init__()

        if self.direction is not None and self.direction != Direction.OUT:
            raise ValueError(f"Direction of out records must be {Direction.OUT!r}")
