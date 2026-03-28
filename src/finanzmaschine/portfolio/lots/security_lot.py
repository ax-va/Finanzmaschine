from typing import TypeVar

from finanzmaschine.portfolio.assets.security import Security
from finanzmaschine.portfolio.infos.security_trade_execution_info import SecurityRecord
from finanzmaschine.portfolio.lots.base_lot import BaseLot

S = TypeVar("S", bound=Security)
R = TypeVar("R", bound=SecurityRecord)


class SecurityLot(BaseLot[S, R]):
    pass
