from dataclasses import dataclass

from finanzmaschine.portfolio.records.security_trade_record import SecurityTradeRecord
from finanzmaschine.portfolio.trade_execution_infos.etp_trade_execution_info import EtpTradeExecutionInfo


@dataclass(frozen=True)
class EtpTradeRecord[I: EtpTradeExecutionInfo](SecurityTradeRecord):
    pass
