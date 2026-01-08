from dataclasses import dataclass

from finanzmaschine.core.lots.base_lot_record import BaseLotRecord


@dataclass(frozen=True)
class ShareLotRecord(BaseLotRecord):
    entitlement: float | None
