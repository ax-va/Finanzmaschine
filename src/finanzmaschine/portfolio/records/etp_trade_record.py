from dataclasses import dataclass

from finanzmaschine.portfolio.records.security_trade_record import SecurityTradeRecord
from finanzmaschine.portfolio.trade_infos.etp_trade_info import EtpTradeInfo


@dataclass(frozen=True)
class EtpTradeRecord[I: EtpTradeInfo](SecurityTradeRecord):
    pass
