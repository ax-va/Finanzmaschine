from dataclasses import dataclass
from typing import override

from finanzmaschine.core.lots.base_lot_record import BaseLotRecord


@dataclass(frozen=True)
class ShareLotRecord(BaseLotRecord):
    entitlement: float | None

    @override
    def validate(self):
        super().validate()
        if self.entitlement is not None:
            assert self.entitlement > 0

    def require_entitlement(self) -> float:
        if self.entitlement is None:
            raise ValueError("Entitlement required")
        return self.entitlement