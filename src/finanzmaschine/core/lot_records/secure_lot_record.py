from dataclasses import dataclass

from finanzmaschine.catalog.broker_enum import Broker
from finanzmaschine.catalog.exchange_enum import Exchange
from finanzmaschine.core.lot_records.base_lot_record import BaseLotRecord


@dataclass(frozen=True)
class SecureLotRecord(BaseLotRecord):
    broker: Broker
    order_id: str
    exchange: Exchange
    trade_id: str
