from dataclasses import dataclass

from finanzmaschine.portfolio.records.crypto_dex_trade_record import CryptoDexTradeRecord


@dataclass(frozen=True, eq=False)
class CryptoDexSwapRecord(CryptoDexTradeRecord):
    pass
