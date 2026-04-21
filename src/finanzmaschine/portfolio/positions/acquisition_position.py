from abc import abstractmethod
from decimal import Decimal
from typing import TypeVar, Generic, List, Tuple

from finanzmaschine.portfolio.assets.asset import Asset
from finanzmaschine.portfolio.lots.acquisition_lot import AcquisitionLot
from finanzmaschine.portfolio.positions.priced_position import PricedPosition
from finanzmaschine.portfolio.records.non_trade_decrease_record import NonTradeDecreaseRecord
from finanzmaschine.portfolio.records.non_trade_increase_record import NonTradeIncreaseRecord
from finanzmaschine.portfolio.records.trade_record import TradeRecord
from finanzmaschine.utils.decimal_helper import safe_sum

A = TypeVar("A", bound=Asset)
D = TypeVar("D", bound=NonTradeDecreaseRecord)
I = TypeVar("I", bound=NonTradeIncreaseRecord)
T = TypeVar("T", bound=TradeRecord)
L = TypeVar("L", bound=AcquisitionLot)


class AcquisitionPosition(PricedPosition[A, D, I | T, L], Generic[A, D, I, T, L]):

    @abstractmethod
    def _create_lot(self, record_in: I | T) -> L:
        pass

    @property
    def cost_basis_sold(self) -> Decimal:
        # workaround for type checker
        lot: AcquisitionLot
        return safe_sum(lot.cost_basis_sold for lot in self._lots_with_records_sold)

    @property
    def proceeds(self) -> Decimal:
        # workaround for type checker
        lot: AcquisitionLot
        return safe_sum(lot.proceeds for lot in self._lots_with_records_sold)

    @property
    def pnl(self) -> Decimal:
        lot: AcquisitionLot
        return safe_sum(lot.pnl for lot in self._lots_with_records_sold)

    @property
    def lots_with_records_sold(self) -> Tuple[L, ...]:
        return tuple(lot for lot in self._lots_with_records_sold)

    @property
    def _lots_with_records_sold(self) -> List[L]:
        return [lot for lot in self._lots_with_records_realized if isinstance(lot, AcquisitionLot)]