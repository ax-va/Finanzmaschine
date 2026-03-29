from typing import TypeVar

from finanzmaschine.portfolio.assets.security import Security
from finanzmaschine.portfolio.lots.base_lot import BaseLot
from finanzmaschine.portfolio.records.base_record import BaseRecord
from finanzmaschine.portfolio.records.security_trade_record import SecurityTradeRecord

S = TypeVar("S", bound=Security)
R = TypeVar("R", bound=BaseRecord)
T = TypeVar("T", bound=SecurityTradeRecord)


class SecurityLot(BaseLot[S, R, T]):
    pass
