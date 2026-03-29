from typing import TypeVar, Generic

from finanzmaschine.portfolio.assets import BaseAsset
from finanzmaschine.portfolio.lots.base_lot import BaseLot
from finanzmaschine.portfolio.records.non_sale_reduction_record import NonSaleReductionRecord
from finanzmaschine.portfolio.records.trade_record import TradeRecord

A = TypeVar('A', bound=BaseAsset)
N = TypeVar("N", bound=NonSaleReductionRecord)
T = TypeVar("T", bound=TradeRecord)


class TradeLot(BaseLot, Generic[A, N, T]):
    pass
