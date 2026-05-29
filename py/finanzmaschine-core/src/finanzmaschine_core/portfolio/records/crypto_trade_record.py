from dataclasses import dataclass

from finanzmaschine_core.portfolio.records import TradeRecord


@dataclass(frozen=True, eq=False)
class CryptoTradeRecord(TradeRecord):
    pass