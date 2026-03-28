from dataclasses import dataclass

from finanzmaschine.core.records.base_record import BaseRecord


@dataclass(frozen=True)
class NonPricedRecord(BaseRecord):
    pass