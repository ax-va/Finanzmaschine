from dataclasses import dataclass

from finanzmaschine.portfolio.records.base_record import BaseRecord, Direction


@dataclass(frozen=True)
class ReductionRecord(BaseRecord):

    def __post_init__(self):
        super().__post_init__()

        if self.direction is not None and self.direction != Direction.OUT:
            raise ValueError(f"Direction of reduction records must be {Direction.OUT!r}")
