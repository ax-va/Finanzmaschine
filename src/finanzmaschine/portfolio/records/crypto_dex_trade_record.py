from dataclasses import dataclass

from finanzmaschine.portfolio.records.crypto_trade_record import CryptoTradeRecord


@dataclass(frozen=True, eq=False)
class CryptoDexTradeRecord(CryptoTradeRecord):
    pass