from typing import TypeVar, Generic

from finanzmaschine.portfolio.assets.security import Security
from finanzmaschine.portfolio.lots.security_lot import SecurityLot
from finanzmaschine.portfolio.operation_types.non_trade_increase_type import NonTradeIncreaseType
from finanzmaschine.portfolio.positions.acquisition_position import AcquisitionPosition
from finanzmaschine.portfolio.records.non_trade_decrease_record import NonTradeDecreaseRecord
from finanzmaschine.portfolio.records.non_trade_increase_record import NonTradeIncreaseRecord
from finanzmaschine.portfolio.records.security_trade_record import SecurityTradeRecord

S = TypeVar("S", bound=Security)
D = TypeVar("D", bound=NonTradeDecreaseRecord)
I = TypeVar("I", bound=NonTradeIncreaseRecord)
T = TypeVar("T", bound=SecurityTradeRecord)
L = TypeVar("L", bound=SecurityLot)


class SecurityPosition(
    AcquisitionPosition[S, NonTradeDecreaseRecord, NonTradeIncreaseRecord[S, NonTradeIncreaseType], T, L],
    Generic[S, T, L],
):
    pass
