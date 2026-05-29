from dataclasses import dataclass

from finanzmaschine_core.portfolio.records.crypto_trade_record import CryptoTradeRecord


@dataclass(frozen=True, eq=False)
class CryptoDexTradeRecord(CryptoTradeRecord):
    pass