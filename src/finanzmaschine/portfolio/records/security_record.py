from dataclasses import dataclass

from finanzmaschine.catalog.broker_enum import Broker
from finanzmaschine.catalog.exchange_enum import Exchange
from finanzmaschine.portfolio.records.base_record import BaseRecord


@dataclass(frozen=True)
class SecurityRecord(BaseRecord):
    broker: Broker
    order_id: str
    exchange: Exchange
    trade_id: str
