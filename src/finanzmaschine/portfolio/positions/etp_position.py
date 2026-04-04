from typing import TypeVar

from finanzmaschine.portfolio.assets.etp import Etp
from finanzmaschine.portfolio.lots import EtpLot
from finanzmaschine.portfolio.positions.security_position import SecurityPosition
from finanzmaschine.portfolio.records.etp_trade_record import EtpTradeRecord

E = TypeVar("E", bound=Etp)
T = TypeVar("T", bound=EtpTradeRecord)
L = TypeVar("L", bound=EtpLot)


class EtpPosition(SecurityPosition[E, T, L]):
    pass
