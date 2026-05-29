from typing import TypeVar, Generic

from finanzmaschine_core.portfolio.assets.security import Security
from finanzmaschine_core.portfolio.lots.acquisition_lot import AcquisitionLot
from finanzmaschine_core.portfolio.operation_types.non_trade_increase_type import NonTradeIncreaseType
from finanzmaschine_core.portfolio.records.non_trade_decrease_record import NonTradeDecreaseRecord
from finanzmaschine_core.portfolio.records.non_trade_increase_record import NonTradeIncreaseRecord
from finanzmaschine_core.portfolio.records.security_trade_record import SecurityTradeRecord

S = TypeVar("S", bound=Security)
T = TypeVar("T", bound=SecurityTradeRecord)


class SecurityLot(
    AcquisitionLot[S, NonTradeDecreaseRecord, T, NonTradeIncreaseRecord[S, NonTradeIncreaseType]],
    Generic[S, T],
):
    pass
