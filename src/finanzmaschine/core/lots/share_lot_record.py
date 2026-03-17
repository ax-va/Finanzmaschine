from dataclasses import dataclass

from finanzmaschine.core.lots.base_lot_record import BaseLotRecord


@dataclass(frozen=True)
class ShareLotRecord(BaseLotRecord):
    entitlement: float | None

    def require_entitlement(self) -> float:
        if self.entitlement is None:
            raise ValueError("Entitlement required")
        return self.entitlement