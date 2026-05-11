from dataclasses import dataclass

from finanzmaschine.portfolio.records.etp_trade_record import EtpTradeRecord


@dataclass(frozen=True, eq=False)
class CryptoEtpTradeRecord(EtpTradeRecord):
    pass
