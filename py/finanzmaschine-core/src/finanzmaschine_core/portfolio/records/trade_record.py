from dataclasses import dataclass
from decimal import Decimal
from typing import Tuple, Self, override

from finanzmaschine_core.portfolio.assets.asset import Asset
from finanzmaschine_core.portfolio.operations.trade_enum import TradeEnum
from finanzmaschine_core.portfolio.records.base_record import BaseRecord
from finanzmaschine_core.portfolio.records.mixins.price_fee_mixin import PriceFeeMixin


@dataclass(frozen=True, eq=False, kw_only=True)
class TradeRecord[Q: Asset](BaseRecord, PriceFeeMixin[Q]):

    def __post_init__(self) -> None:
        if not isinstance(self.operation.variant, TradeEnum):
            raise ValueError("Operation variant in `TradeRecord` must be of the `TradeEnum` type")

        BaseRecord.__post_init__(self)
        PriceFeeMixin.__post_init__(self)

    @override
    def split(self, quantity: Decimal) -> Tuple[Self, Self]:
        return PriceFeeMixin.split(self, quantity)
