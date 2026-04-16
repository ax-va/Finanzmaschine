from decimal import Decimal
from typing import TypeVar, Generic, List, FrozenSet, Tuple

from finanzmaschine.portfolio.assets.asset import Asset
from finanzmaschine.portfolio.lots.priced_lot import PricedLot
from finanzmaschine.portfolio.records.non_trade_decrease_record import NonTradeDecreaseRecord
from finanzmaschine.portfolio.records.non_trade_increase_record import NonTradeIncreaseRecord
from finanzmaschine.portfolio.records.trade_record import TradeRecord
from finanzmaschine.utils.decimal_helper import safe_sum, round_to_quantum

A = TypeVar('A', bound=Asset)
D = TypeVar("D", bound=NonTradeDecreaseRecord)
I = TypeVar("I", bound=NonTradeIncreaseRecord)
T = TypeVar("T", bound=TradeRecord)


class AcquisitionLot(PricedLot[A, D | T, I | T], Generic[A, D, T, I]):

    @property
    def quantity_sold(self) -> Decimal:
        return round_to_quantum(
            safe_sum(r_out.quantity for r_out in self._records_sold),
            self.base_asset.quantum,
        )

    @property
    def records_sold(self) -> Tuple[T, ...]:
        return tuple(self._records_sold)

    @property
    def quote_assets_sold(self) -> FrozenSet[A]:
        return frozenset(r_out.quote_asset for r_out in self._records_sold)

    @property
    def quote_assets(self) -> FrozenSet[A]:
        asset_set = set(self.quote_assets_sold)
        asset_set.add(self.record_in.quote_asset)
        return frozenset(asset_set)

    @property
    def cost_basis_sold(self) -> Decimal:
        if self.is_closed:
            return self.cost_basis
        # workaround for typechecker
        record_in: TradeRecord = self._record_in
        return round_to_quantum(
            self.quantity_sold / record_in.quantity * self.cost_basis,
            self.record_in.quote_asset.quantum,
        )

    @property
    def proceeds(self) -> Decimal:
        self.ensure_one_quote_asset()
        # workaround for type checker
        r_out: TradeRecord
        return safe_sum(r_out.gross_value - r_out.fee for r_out in self._records_sold)

    @property
    def pnl(self) -> Decimal:
        """Profit and loss (PnL)"""
        return self.proceeds - self.cost_basis_sold

    @property
    def _records_sold(self) -> List[T]:
        return [r_out for r_out in self._records_realized if isinstance(r_out, TradeRecord)]
