from dataclasses import dataclass
from decimal import Decimal

from finanzmaschine_core.catalog.aggregator_enum import AggregatorEnum
from finanzmaschine_core.catalog.broker_enum import BrokerEnum
from finanzmaschine_core.portfolio.assets.asset import Asset

PriceSource = BrokerEnum | AggregatorEnum


@dataclass(frozen=True, eq=False, kw_only=True)
class PriceMixin[Q: Asset]:
    quote_asset: Q
    price: Decimal
    price_source: PriceSource

    def __post_init__(self) -> None:
        if not (self.price > Decimal("0")):
            raise ValueError("Price must be positive")

    @property
    def gross_value(self) -> Decimal:
        return self.quantity * self.price
