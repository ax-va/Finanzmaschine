from dataclasses import dataclass

from finanzmaschine.portfolio.records.priced_record import PricedRecord
from finanzmaschine.portfolio.trade_infos.security_trade_info import SecurityTradeInfo


@dataclass(frozen=True)
class SecurityTradeRecord[I: SecurityTradeInfo](PricedRecord):
    execution_info: I
