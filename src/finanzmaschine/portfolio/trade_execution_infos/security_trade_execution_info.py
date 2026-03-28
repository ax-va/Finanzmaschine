from dataclasses import dataclass

from finanzmaschine.catalog.broker_enum import Broker
from finanzmaschine.catalog.exchange_enum import Exchange


@dataclass(frozen=True)
class SecurityTradeExecutionInfo:
    broker: Broker
    order_id: str
    exchange: Exchange
    trade_id: str
