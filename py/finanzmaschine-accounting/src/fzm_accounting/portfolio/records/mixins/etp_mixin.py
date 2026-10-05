from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, eq=False, kw_only=True)
class EtpMixin:
    entitlement: Decimal | None

    def __post_init__(self) -> None:
        if self.entitlement is not None and not (self.entitlement > 0):
            raise ValueError("Specified entitlement must be positive")

    def ensure_entitlement(self) -> Decimal:
        if self.entitlement is None:
            raise ValueError("Entitlement required")
        return self.entitlement