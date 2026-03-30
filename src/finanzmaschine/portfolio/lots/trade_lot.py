from typing import TypeVar

from finanzmaschine.portfolio.assets import BaseAsset
from finanzmaschine.portfolio.lots.priced_lot import PricedLot
from finanzmaschine.portfolio.records.non_sale_reduction_record import NonSaleReductionRecord
from finanzmaschine.portfolio.records.trade_record import TradeRecord

A = TypeVar('A', bound=BaseAsset)
N = TypeVar("N", bound=NonSaleReductionRecord)
T = TypeVar("T", bound=TradeRecord)


class TradeLot(PricedLot[A, N | T, T]):
    pass
