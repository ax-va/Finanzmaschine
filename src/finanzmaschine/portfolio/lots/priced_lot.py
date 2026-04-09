from typing import TypeVar, Generic, List, Tuple, Set

from finanzmaschine.portfolio.assets.asset import Asset
from finanzmaschine.portfolio.lots.base_lot import BaseLot
from finanzmaschine.portfolio.records.non_trade_decrease_record import NonTradeDecreaseRecord
from finanzmaschine.portfolio.records.priced_record import PricedRecord
from finanzmaschine.utils.float_helper import safe_sum

A = TypeVar('A', bound=Asset)
D = TypeVar("D", bound=NonTradeDecreaseRecord)
P = TypeVar("P", bound=PricedRecord)


class PricedLot(BaseLot[A, D | P, P], Generic[A, D, P]):

    @property
    def quantity_realized(self) -> float:
        return safe_sum(r_out.quantity for r_out in self._records_realized)

    @property
    def cost_basis(self) -> float:
        # workaround for typechecker
        record_in: PricedRecord = self._record_in
        return record_in.gross_value + record_in.fee

    @property
    def cost_basis_per_unit(self) -> float:
        # workaround for typechecker
        record_in: PricedRecord = self._record_in
        return self.cost_basis / record_in.quantity

    @property
    def cost_basis_realized(self) -> float:
        return self.quantity_realized * self.cost_basis_per_unit

    @property
    def records_realized(self) -> Tuple[P, ...]:
        return tuple(r_out for r_out in self._records_realized)

    @property
    def quote_assets_realized(self) -> frozenset[A]:
        return frozenset(r_out.quote_asset for r_out in self._records_realized)

    @property
    def quote_assets(self) -> frozenset[A]:
        asset_set = set(self.quote_assets_realized)
        asset_set.add(self.record_in.quote_asset)
        return frozenset(asset_set)

    @property
    def _records_realized(self) -> List[P]:
        return [r_out for r_out in self._records_out if isinstance(r_out, PricedRecord)]

    def ensure_one_quote_asset(self):
        if len(self.quote_assets) > 0:
            raise ValueError(f"Lot contains reports-out with more than one quote asset: {self.quote_assets}")
