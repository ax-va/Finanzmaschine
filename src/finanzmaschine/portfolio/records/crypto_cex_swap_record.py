from dataclasses import dataclass

from finanzmaschine.portfolio.records.crypto_cex_trade_record import CryptoCexTradeRecord

@dataclass(frozen=True, eq=False)
class CryptoCexSwapRecord(CryptoCexTradeRecord):
    pass