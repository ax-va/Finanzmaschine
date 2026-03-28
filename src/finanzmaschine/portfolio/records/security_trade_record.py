from dataclasses import dataclass

from finanzmaschine.portfolio.records.priced_record import PricedRecord
from finanzmaschine.portfolio.trade_execution_infos.security_trade_execution_info import SecurityTradeExecutionInfo


@dataclass(frozen=True)
class SecurityTradeRecord[I: SecurityTradeExecutionInfo](PricedRecord):
    execution_info: I
