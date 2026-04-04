from typing import TypeVar

from finanzmaschine.portfolio.assets.etp import Etp
from finanzmaschine.portfolio.lots import EtpLot
from finanzmaschine.portfolio.positions.security_position import SecurityPosition
from finanzmaschine.portfolio.records.etp_trade_record import EtpTradeRecord
from finanzmaschine.portfolio.records.non_trade_decrease_record import NonTradeDecreaseRecord
from finanzmaschine.portfolio.records.non_trade_increase_record import NonTradeIncreaseRecord

E = TypeVar("E", bound=Etp)
D = TypeVar("D", bound=NonTradeDecreaseRecord)
I = TypeVar("I", bound=NonTradeIncreaseRecord)
T = TypeVar("T", bound=EtpTradeRecord)
L = TypeVar("L", bound=EtpLot)


class EtpPosition(SecurityPosition[E, D, I, T, L]):
    pass
