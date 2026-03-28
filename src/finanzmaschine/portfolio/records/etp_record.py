from dataclasses import dataclass

from finanzmaschine.portfolio.records.security_record import SecurityRecord


@dataclass(frozen=True)
class EtpRecord(SecurityRecord):
    entitlement: float | None

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.entitlement is not None and not (self.entitlement > 0):
            raise ValueError("Specified entitlement must be positive")

    def require_entitlement(self) -> float:
        if self.entitlement is None:
            raise ValueError("Entitlement required")
        return self.entitlement