from typing import TypeVar

from finanzmaschine.portfolio.assets.security import Security
from finanzmaschine.portfolio.lots.base_lot import BaseLot
from finanzmaschine.portfolio.records.non_sale_reduction_record import NonSaleReductionRecord
from finanzmaschine.portfolio.records.security_trade_record import SecurityTradeRecord

S = TypeVar("S", bound=Security)
N = TypeVar("N", bound=NonSaleReductionRecord)
T = TypeVar("T", bound=SecurityTradeRecord)


class SecurityLot(BaseLot[S, N, T]):
    pass
