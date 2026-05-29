from dataclasses import dataclass

from finanzmaschine_core.portfolio.records.etp_trade_record import EtpTradeRecord


@dataclass(frozen=True, eq=False)
class CryptoEtpTradeRecord(EtpTradeRecord):
    pass
