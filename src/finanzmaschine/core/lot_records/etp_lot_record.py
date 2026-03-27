from dataclasses import dataclass

from finanzmaschine.core.lot_records.base_lot_record import BaseLotRecord


@dataclass(frozen=True)
class EtpLotRecord(BaseLotRecord):
    entitlement: float | None

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.entitlement is not None and not (self.entitlement > 0):
            raise ValueError("`entitlement` must be positive if not `None`")

    def require_entitlement(self) -> float:
        if self.entitlement is None:
            raise ValueError("Entitlement required")
        return self.entitlement