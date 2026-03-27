from typing import TypeVar

from finanzmaschine.core.assets.security import Security
from finanzmaschine.core.records.security_record import SecurityRecord
from finanzmaschine.core.lots.base_lot import BaseLot

S = TypeVar("S", bound=Security)
R = TypeVar("R", bound=SecurityRecord)


class SecurityLot(BaseLot[S, R]):
    pass
