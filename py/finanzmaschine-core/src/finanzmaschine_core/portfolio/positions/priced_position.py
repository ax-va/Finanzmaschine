from decimal import Decimal
from types import MappingProxyType
from typing import Dict, Tuple

from finanzmaschine_core.helpers.decimal_helper import safe_sum
from finanzmaschine_core.portfolio.assets.asset import Asset
from finanzmaschine_core.portfolio.lots.priced_lot import PricedLot, RecordIn, RecordRealized, RecordOut, RecordSold
from finanzmaschine_core.portfolio.positions.base_position import BasePosition


class PricedPosition[A: Asset, L: PricedLot](BasePosition[A, RecordIn, RecordOut, L]):

    @property
    def lot_by_record_realized(self) -> MappingProxyType[RecordRealized, L]:
        return MappingProxyType(self._lot_by_record_out)

    @property
    def lot_by_record_sold(self) -> MappingProxyType[RecordSold, L]:
        return MappingProxyType(self._lot_by_record_sold)

    @property
    def cost_basis_realized(self) -> Decimal:
        # workaround for type checker
        lot: PricedLot
        return safe_sum(lot.cost_basis_realized for lot in self._lots_with_records_realized)

    @property
    def cost_basis_sold(self) -> Decimal:
        # workaround for type checker
        lot: PricedLot
        return safe_sum(lot.cost_basis_sold for lot in self._lots_with_records_sold)

    @property
    def proceeds_realized(self) -> Decimal:
        # workaround for type checker
        lot: PricedLot
        return safe_sum(lot.proceeds_realized for lot in self._lots_with_records_realized)

    @property
    def proceeds_sold(self) -> Decimal:
        # workaround for type checker
        lot: PricedLot
        return safe_sum(lot.proceeds_sold for lot in self._lots_with_records_sold)

    @property
    def pnl_realized(self) -> Decimal:
        # workaround for type checker
        lot: PricedLot
        return safe_sum(lot.pnl_realized for lot in self._lots_with_records_realized)

    @property
    def pnl_sold(self) -> Decimal:
        # workaround for type checker
        lot: PricedLot
        return safe_sum(lot.pnl_sold for lot in self._lots_with_records_sold)

    @property
    def _lot_by_record_realized(self) -> Dict[RecordRealized, L]:
        return {record: lot for record, lot in self._lot_by_record_out.items() if isinstance(record, RecordRealized)}

    @property
    def _lot_by_record_sold(self) -> Dict[RecordSold, L]:
        return {record: lot for record, lot in self._lot_by_record_realized.items() if isinstance(record, RecordSold)}

    @property
    def _lots_with_records_realized(self) -> Tuple[L, ...]:
        return tuple(dict.fromkeys(self._lot_by_record_realized.values()))

    @property
    def _lots_with_records_sold(self) -> Tuple[L, ...]:
        return tuple(dict.fromkeys(self._lot_by_record_sold.values()))

    def _create_lot(self, record_in: RecordIn) -> PricedLot:
        return PricedLot(base_asset=self.base_asset, record_in=record_in)
