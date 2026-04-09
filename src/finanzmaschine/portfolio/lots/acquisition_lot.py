from typing import TypeVar, Generic, List, Set

from finanzmaschine.portfolio.assets.asset import Asset
from finanzmaschine.portfolio.lots.priced_lot import PricedLot
from finanzmaschine.portfolio.operation_types.trade_type import TradeType
from finanzmaschine.portfolio.records.non_trade_decrease_record import NonTradeDecreaseRecord
from finanzmaschine.portfolio.records.non_trade_increase_record import NonTradeIncreaseRecord
from finanzmaschine.portfolio.records.trade_record import TradeRecord
from finanzmaschine.utils.float_helper import safe_sum

A = TypeVar('A', bound=Asset)
D = TypeVar("D", bound=NonTradeDecreaseRecord)
I = TypeVar("I", bound=NonTradeIncreaseRecord)
T = TypeVar("T", bound=TradeRecord)


class AcquisitionLot(PricedLot[A, D | T, I | T], Generic[A, D, T, I]):

    @property
    def _records_out_sold(self) -> List[T]:
        return [
            r_out for r_out in self._records_out_realized
            if isinstance(r_out, TradeRecord) and r_out.operation_type == TradeType.SELL
        ]

    @property
    def _quote_assets_sold(self) -> frozenset[A]:
        return frozenset(r_out.quote_asset for r_out in self._records_out_sold)
