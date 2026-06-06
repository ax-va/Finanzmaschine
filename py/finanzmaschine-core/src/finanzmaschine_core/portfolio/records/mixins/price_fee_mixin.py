from dataclasses import dataclass
from decimal import Decimal
from typing import Tuple, Self

from finanzmaschine_core.helpers.decimal_helper import round_to_quantum
from finanzmaschine_core.portfolio.assets.asset import Asset
from finanzmaschine_core.portfolio.operations.direction_enum import DirectionEnum
from finanzmaschine_core.portfolio.records.mixins.fee_mixin import FeeMixin
from finanzmaschine_core.portfolio.records.mixins.price_mixin import PriceMixin


@dataclass(frozen=True, eq=False, kw_only=True)
class PriceFeeMixin[Q: Asset](PriceMixin[Q], FeeMixin):

    def __post_init__(self) -> None:
        PriceMixin.__post_init__(self)
        FeeMixin.__post_init__(self)

    @property
    def quote_asset_flow_out(self) -> Decimal:
        return -(self.gross_value + self.fee)

    @property
    def quote_asset_flow_in(self) -> Decimal:
        return self.gross_value - self.fee

    @property
    def quote_asset_flow(self) -> Decimal:
        return {
            DirectionEnum.IN: self.quote_asset_flow_out,
            DirectionEnum.OUT: self.quote_asset_flow_in,
        }[self.operation.direction]

    def split(self, quantity: Decimal) -> Tuple[Self, Self]:
        ratio: Decimal = quantity / self.quantity
        fee_closing = round_to_quantum(ratio * self.fee, quantum=self.quote_asset.quantum)
        fee_remaining = self.fee - fee_closing
        return (
            self.copy(quantity=quantity, fee=fee_closing),
            self.copy(quantity=self.quantity - quantity, fee=fee_remaining),
        )
