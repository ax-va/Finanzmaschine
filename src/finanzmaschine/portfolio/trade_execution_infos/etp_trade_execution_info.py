from dataclasses import dataclass

from finanzmaschine.portfolio.trade_execution_infos.security_trade_execution_info import SecurityTradeExecutionInfo


@dataclass(frozen=True)
class EtpTradeExecutionInfo(SecurityTradeExecutionInfo):
    entitlement: float | None

    def __post_init__(self) -> None:
        if self.entitlement is not None and not (self.entitlement > 0):
            raise ValueError("Specified entitlement must be positive")

    def require_entitlement(self) -> float:
        if self.entitlement is None:
            raise ValueError("Entitlement required")
        return self.entitlement