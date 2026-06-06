from dataclasses import dataclass

from finanzmaschine_core.catalog.counterparty_enum import CounterpartyEnum


@dataclass(frozen=True, eq=False, kw_only=True)
class CounterpartyMixin:
    counterparty: CounterpartyEnum
    trade_id: str
