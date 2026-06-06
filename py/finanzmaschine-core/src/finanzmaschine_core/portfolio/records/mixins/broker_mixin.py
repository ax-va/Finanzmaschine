from dataclasses import dataclass

from finanzmaschine_core.catalog.broker_enum import BrokerEnum


@dataclass(frozen=True, eq=False, kw_only=True)
class BrokerMixin:
    broker: BrokerEnum
    account_id: str
