from dataclasses import dataclass
from typing import TypeVar

from finanzmaschine.catalog.broker_enum import Broker
from finanzmaschine.catalog.exchange_enum import Exchange
from finanzmaschine.portfolio.records.trade_record import TradeRecord


@dataclass(frozen=True)
class SecurityTradeRecord(TradeRecord):
    broker: Broker
    order_id: str
    exchange: Exchange
    trade_id: str
