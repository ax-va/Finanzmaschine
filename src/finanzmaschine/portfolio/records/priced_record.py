from dataclasses import dataclass
from decimal import Decimal
from typing import Tuple, Self, override

from finanzmaschine.portfolio.assets.asset import Asset
from finanzmaschine.portfolio.fees.fee import Fee
from finanzmaschine.portfolio.fees.fee_component import FeeComponent
from finanzmaschine.portfolio.operation_types.priced_operation_type import PricedOperationType
from finanzmaschine.portfolio.records.base_record import BaseRecord, Direction
from finanzmaschine.utils.decimal_helper import round_to_quantum


@dataclass(frozen=True, eq=False)
class PricedRecord[Q: Asset, T: PricedOperationType](BaseRecord[T]):
    quote_asset: Q
    price: Decimal
    fee: Fee

    def __post_init__(self) -> None:
        super().__post_init__()

        if not (self.price > Decimal("0")):
            raise ValueError("Price must be positive")

    @property
    def gross_value(self) -> Decimal:
        return self.quantity * self.price

    @property
    def quote_asset_flow(self) -> Decimal:
        if self.direction == Direction.IN:
            return -(self.gross_value + self.fee.get_total(self.quote_asset))
        elif self.direction == Direction.OUT:
            return self.gross_value - self.fee.get_total(self.quote_asset)
        else:
            raise ValueError("Direction is not specified")

    @override
    def split(self, quantity: Decimal) -> Tuple[Self, Self]:
        ratio: Decimal = quantity / self.quantity
        fee_closing = Fee(
            tuple(
                FeeComponent(
                    amount=round_to_quantum(ratio * c.amount, c.asset.quantum),
                    asset=c.asset,
                ) for c in self.fee.components
            )
        )
        fee_remaining = Fee(
            tuple(
                FeeComponent(
                    amount=c.amount - c_closing.amount,
                    asset=c.asset,
                ) for c, c_closing in zip(self.fee.components, fee_closing.components)
            )
        )
        return (
            self.copy(quantity=quantity, fee=fee_closing),
            self.copy(quantity=self.quantity - quantity, fee=fee_remaining),
        )
