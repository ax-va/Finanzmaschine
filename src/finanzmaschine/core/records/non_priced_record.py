from dataclasses import dataclass
from enum import StrEnum

from finanzmaschine.core.records.base_record import BaseRecord


class Reason(StrEnum):
    TRANSFER = "TRANSFER"


@dataclass(frozen=True)
class NonPricedRecord(BaseRecord):
    reason: Reason | None
