from dataclasses import dataclass

from finanzmaschine.portfolio.records import TradeRecord


@dataclass(frozen=True, eq=False)
class CryptoTradeRecord(TradeRecord):
    pass