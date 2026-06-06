from decimal import Decimal
from typing import List, Tuple, FrozenSet, Set

from finanzmaschine_core.portfolio.assets.asset import Asset
from finanzmaschine_core.portfolio.lots.base_lot import BaseLot
from finanzmaschine_core.portfolio.records.income_record import IncomeRecord
from finanzmaschine_core.helpers.decimal_helper import safe_sum, round_to_quantum
from finanzmaschine_core.portfolio.records.trade_record import TradeRecord

RecordIn = TradeRecord | IncomeRecord
RecordOut = TradeRecord
RecordRealized = TradeRecord
RecordSold = TradeRecord

class PricedLot[A: Asset](BaseLot[A, RecordIn, RecordOut]):

    @property
    def cost_basis(self) -> Decimal:
        # workaround for typechecker
        record_in: RecordIn = self._record_in
        return round_to_quantum(
            value=abs(record_in.quote_asset_flow_out)
            if hasattr(record_in, "fee")
            else record_in.gross_value,
            quantum=record_in.quote_asset.quantum,
        )

    @property
    def cost_basis_per_unit(self) -> Decimal:
        return self.cost_basis / self._record_in.quantity

    @property
    def records_realized(self) -> Tuple[RecordRealized, ...]:
        return tuple(r_out for r_out in self._records_realized)

    @property
    def records_sold(self) -> Tuple[RecordSold, ...]:
        return tuple(r_out for r_out in self._records_sold)

    @property
    def quote_assets_realized(self) -> FrozenSet[A]:
        return frozenset(self._quote_assets_realized)

    @property
    def quote_assets_sold(self) -> FrozenSet[A]:
        return frozenset(self._quote_assets_sold)

    @property
    def single_quote_asset_realized(self) -> A:
        if len(self._quote_assets_realized) > 1:
            raise ValueError(f"More than one quote asset for realized quantity: {self._quote_assets_realized}")
        return self.record_in.quote_asset

    @property
    def single_quote_asset_sold(self) -> A:
        if len(self._quote_assets_sold) > 1:
            raise ValueError(f"More than one quote asset for sold quantity: {self._quote_assets_sold}")
        return self.record_in.quote_asset

    @property
    def quantity_realized(self) -> Decimal:
        return safe_sum(r_out.quantity for r_out in self._records_realized)

    @property
    def quantity_sold(self) -> Decimal:
        return safe_sum(r_out.quantity for r_out in self._records_sold)

    @property
    def cost_basis_realized(self) -> Decimal:
        return round_to_quantum(
            value=self.quantity_realized * self.cost_basis_per_unit
            if self.quantity_realized < self._record_in.quantity
            else self.cost_basis,
            quantum=self._record_in.quote_asset.quantum,
        )

    @property
    def cost_basis_sold(self) -> Decimal:
        return round_to_quantum(
            value=self.quantity_sold * self.cost_basis_per_unit
            if self.quantity_sold < self._record_in.quantity
            else self.cost_basis,
            quantum=self._record_in.quote_asset.quantum,
        )

    @property
    def proceeds_realized(self) -> Decimal:
        return round_to_quantum(
            value=safe_sum(
                r_out.quote_asset_flow_in
                if hasattr(r_out, "fee")
                else r_out.gross_value
                for r_out in self._records_realized
            ),
            quantum=self.single_quote_asset_realized.quantum
        )

    @property
    def proceeds_sold(self) -> Decimal:
        return round_to_quantum(
            value=safe_sum(
                r_out.quote_asset_flow_in
                if hasattr(r_out, "fee")
                else r_out.gross_value
                for r_out in self._records_sold
            ),
            quantum=self.single_quote_asset_sold.quantum
        )

    @property
    def pnl_realized(self) -> Decimal:
        """Profit and loss (PnL)"""
        if self.single_quote_asset_realized != self.record_in.quote_asset:
            raise ValueError(
                f"Different quote assets for realized proceeds and cost basis, respectively: "
                f"{self.single_quote_asset_realized} and {self.record_in.quote_asset}"
            )
        return self.proceeds_realized - self.cost_basis_realized

    @property
    def pnl_sold(self) -> Decimal:
        """Profit and loss (PnL)"""
        if self.single_quote_asset_sold != self.record_in.quote_asset:
            raise ValueError(
                f"Different quote assets for sold proceeds and cost basis, respectively: "
                f"{self.single_quote_asset_sold} and {self.record_in.quote_asset}"
            )
        return self.proceeds_realized - self.cost_basis_realized

    @property
    def _quote_assets_realized(self) -> Set[A]:
        return set(r_out.quote_asset for r_out in self._records_realized)

    @property
    def _quote_assets_sold(self) -> Set[A]:
        return set(r_out.quote_asset for r_out in self._records_sold)

    @property
    def _records_realized(self) -> List[RecordRealized]:
        return [r_out for r_out in self._records_out if isinstance(r_out, RecordRealized)]

    @property
    def _records_sold(self) -> List[RecordSold]:
        return [r_out for r_out in self._records_realized if isinstance(r_out, RecordSold)]
