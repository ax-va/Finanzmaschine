from dataclasses import dataclass

from finanzmaschine.portfolio.records.trade_record import TradeRecord
from finanzmaschine.portfolio.record_infos.security_trade_execution_info import SecurityTradeExecutionInfo


@dataclass(frozen=True)
class SecurityTradeRecord(TradeRecord):
    execution_info: SecurityTradeExecutionInfo
