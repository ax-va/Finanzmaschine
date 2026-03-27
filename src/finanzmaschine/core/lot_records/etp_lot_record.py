from dataclasses import dataclass

from finanzmaschine.core.lot_records.secure_lot_record import SecureLotRecord


@dataclass(frozen=True)
class EtpLotRecord(SecureLotRecord):
    entitlement: float | None

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.entitlement is not None and not (self.entitlement > 0):
            raise ValueError("`entitlement` must be positive if not `None`")

    def require_entitlement(self) -> float:
        if self.entitlement is None:
            raise ValueError("Entitlement required")
        return self.entitlement