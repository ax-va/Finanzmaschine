from dataclasses import dataclass

from finanzmaschine_core.catalog.exchange_enum import ExchangeEnum


@dataclass(frozen=True, eq=False, kw_only=True)
class ExchangeMixin:
    exchange: ExchangeEnum
    trade_id: str
