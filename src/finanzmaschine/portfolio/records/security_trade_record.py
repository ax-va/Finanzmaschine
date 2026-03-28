from dataclasses import dataclass

from finanzmaschine.portfolio.records.priced_record import PricedRecord
from finanzmaschine.portfolio.infos.security_trade_execution_info import SecurityTradeExecutionInfo


@dataclass(frozen=True)
class SecurityTradeRecord(PricedRecord):
    execution_info: SecurityTradeExecutionInfo
