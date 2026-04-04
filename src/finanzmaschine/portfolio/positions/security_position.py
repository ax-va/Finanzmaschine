from typing import TypeVar

from finanzmaschine.portfolio.assets.security import Security
from finanzmaschine.portfolio.lots.security_lot import SecurityLot
from finanzmaschine.portfolio.positions.acquisition_position import AcquisitionPosition
from finanzmaschine.portfolio.records.non_trade_decrease_record import NonTradeDecreaseRecord
from finanzmaschine.portfolio.records.non_trade_increase_record import NonTradeIncreaseRecord
from finanzmaschine.portfolio.records.security_trade_record import SecurityTradeRecord

S = TypeVar("S", bound=Security)
D = TypeVar("D", bound=NonTradeDecreaseRecord)
I = TypeVar("I", bound=NonTradeIncreaseRecord)
T = TypeVar("T", bound=SecurityTradeRecord)
L = TypeVar("L", bound=SecurityLot)


class SecurityPosition(AcquisitionPosition[S, D, I, T, L]):
    pass
