from decimal import Decimal
from typing import TypeVar, Generic, List, Tuple, FrozenSet

from finanzmaschine.portfolio.assets.asset import Asset
from finanzmaschine.portfolio.lots.base_lot import BaseLot
from finanzmaschine.portfolio.records.non_trade_decrease_record import NonTradeDecreaseRecord
from finanzmaschine.portfolio.records.priced_record import PricedRecord
from finanzmaschine.utils.decimal_helper import safe_sum, round_to_quantum

A = TypeVar('A', bound=Asset)
D = TypeVar("D", bound=NonTradeDecreaseRecord)
P = TypeVar("P", bound=PricedRecord)


class PricedLot(BaseLot[A, D | P, P], Generic[A, D, P]):

    @property
    def quantity_realized(self) -> Decimal:
        return round_to_quantum(
            safe_sum(r_out.quantity for r_out in self._records_realized),
            self.base_asset.quantum,
        )

    @property
    def cost_basis(self) -> Decimal:
        # workaround for typechecker
        record_in: PricedRecord = self._record_in
        return round_to_quantum(record_in.gross_value + record_in.fee, record_in.quote_asset.quantum)

    @property
    def cost_basis_per_unit(self) -> Decimal:
        # workaround for typechecker
        record_in: PricedRecord = self._record_in
        return round_to_quantum(
            self.cost_basis / record_in.quantity,
            record_in.quote_asset.quantum,
        )

    @property
    def cost_basis_realized(self) -> Decimal:
        return self.quantity_realized * self.cost_basis_per_unit

    @property
    def records_realized(self) -> Tuple[P, ...]:
        return tuple(r_out for r_out in self._records_realized)

    @property
    def quote_assets_realized(self) -> FrozenSet[A]:
        return frozenset(r_out.quote_asset for r_out in self._records_realized)

    @property
    def quote_assets(self) -> FrozenSet[A]:
        asset_set = set(self.quote_assets_realized)
        asset_set.add(self.record_in.quote_asset)
        return frozenset(asset_set)

    @property
    def _records_realized(self) -> List[P]:
        return [r_out for r_out in self._records_out if isinstance(r_out, PricedRecord)]

    def ensure_one_quote_asset(self):
        if len(self.quote_assets) > 1:
            raise ValueError(f"More than one quote asset: {self.quote_assets}")
