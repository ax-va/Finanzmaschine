from typing import TypeVar, Generic

from finanzmaschine.portfolio.assets import BaseAsset
from finanzmaschine.portfolio.lots.priced_lot import PricedLot
from finanzmaschine.portfolio.records.non_trade_decrease_record import NonTradeDecreaseRecord
from finanzmaschine.portfolio.records.non_trade_increase_record import NonTradeIncreaseRecord
from finanzmaschine.portfolio.records.trade_record import TradeRecord
from finanzmaschine.utils.float_helper import safe_sum

A = TypeVar('A', bound=BaseAsset)
D = TypeVar("D", bound=NonTradeDecreaseRecord)
I = TypeVar("I", bound=NonTradeIncreaseRecord)
T = TypeVar("T", bound=TradeRecord)


class AcquisitionLot(PricedLot[A, D | T, I | T], Generic[A, D, T, I]):

    @property
    def quantity_sale(self) -> float:
        return safe_sum(r_out.quantity for r_out in self.records_out if isinstance(r_out, TradeRecord))
