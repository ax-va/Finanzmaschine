from typing import TypeVar

from finanzmaschine.portfolio.assets.security import Security
from finanzmaschine.portfolio.lots.trade_lot import TradeLot
from finanzmaschine.portfolio.records.non_sale_reduction_record import NonSaleReductionRecord
from finanzmaschine.portfolio.records.security_trade_record import SecurityTradeRecord

S = TypeVar("S", bound=Security)
N = TypeVar("N", bound=NonSaleReductionRecord)
T = TypeVar("T", bound=SecurityTradeRecord)


class SecurityLot(TradeLot[S, N | T, T]):
    pass
