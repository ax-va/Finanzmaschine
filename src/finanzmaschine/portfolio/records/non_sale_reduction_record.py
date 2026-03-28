from dataclasses import dataclass
from enum import StrEnum

from finanzmaschine.portfolio.records.base_record import BaseRecord, Direction


class ReductionReason(StrEnum):
    TRANSFER_OUT = "TRANSFER_OUT"


@dataclass(frozen=True)
class NonSaleReductionRecord(BaseRecord):
    reason: ReductionReason

    def __post_init__(self):
        super().__post_init__()

        if self.direction is not None and self.direction != Direction.OUT:
            raise ValueError(f"Direction of reduction records must be {Direction.OUT!r}")
