from abc import abstractmethod
from types import MappingProxyType
from typing import TypeVar, Generic, Dict

from finanzmaschine.portfolio.assets.asset import Asset
from finanzmaschine.portfolio.lots.priced_lot import PricedLot
from finanzmaschine.portfolio.positions.base_position import BasePosition
from finanzmaschine.portfolio.records.non_trade_decrease_record import NonTradeDecreaseRecord
from finanzmaschine.portfolio.records.priced_record import PricedRecord

A = TypeVar("A", bound=Asset)
D = TypeVar("D", bound=NonTradeDecreaseRecord)
P = TypeVar("P", bound=PricedRecord)
L = TypeVar("L", bound=PricedLot)


class PricedPosition(BasePosition[A, D | P, L], Generic[A, D, P, L]):

    @abstractmethod
    def _create_lot(self, record_in: P) -> L:
        pass

    @property
    def lot_by_record_realized(self) -> MappingProxyType[P, L]:
        return MappingProxyType(self._lot_by_record_out)

    @property
    def _lot_by_record_realized(self) -> Dict[P, L]:
        return {record: lot for record, lot in self._lot_by_record_out.items() if isinstance(lot, PricedLot)}
