from typing import TypeVar

from finanzmaschine.portfolio.assets import BaseAsset
from finanzmaschine.portfolio.lots.priced_lot import PricedLot
from finanzmaschine.portfolio.records.non_sale_reduction_record import NonSaleReductionRecord
from finanzmaschine.portfolio.records.trade_record import TradeRecord
from finanzmaschine.utils.float_helper import safe_sum

A = TypeVar('A', bound=BaseAsset)
N = TypeVar("N", bound=NonSaleReductionRecord)
T = TypeVar("T", bound=TradeRecord)


class TradeLot(PricedLot[A, N | T, T]):

    @property
    def quantity_sale(self) -> float:
        return safe_sum(r_out.quantity for r_out in self.records_out if isinstance(r_out, TradeRecord))
