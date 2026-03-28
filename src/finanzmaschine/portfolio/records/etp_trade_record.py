from dataclasses import dataclass

from finanzmaschine.portfolio.records.security_trade_record import SecurityTradeRecord


@dataclass(frozen=True)
class EtpTradeRecord(SecurityTradeRecord):
    entitlement: float | None

    def __post_init__(self) -> None:
        if self.entitlement is not None and not (self.entitlement > 0):
            raise ValueError("Specified entitlement must be positive")

    def require_entitlement(self) -> float:
        if self.entitlement is None:
            raise ValueError("Entitlement required")
        return self.entitlement
