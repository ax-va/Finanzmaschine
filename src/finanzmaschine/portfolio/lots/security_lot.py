from typing import TypeVar

from finanzmaschine.portfolio.assets.security import Security
from finanzmaschine.portfolio.records.security_record import SecurityRecord
from finanzmaschine.portfolio.lots.base_lot import BaseLot

S = TypeVar("S", bound=Security)
R = TypeVar("R", bound=SecurityRecord)


class SecurityLot(BaseLot[S, R]):
    pass
