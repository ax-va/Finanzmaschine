from dataclasses import dataclass

from finanzmaschine_core.catalog.broker_enum import Broker
from finanzmaschine_core.catalog.exchange_enum import Exchange
from finanzmaschine_core.portfolio.records.trade_record import TradeRecord


@dataclass(frozen=True, eq=False)
class SecurityTradeRecord(TradeRecord):
    broker: Broker
    order_id: str
    exchange: Exchange
    trade_id: str
