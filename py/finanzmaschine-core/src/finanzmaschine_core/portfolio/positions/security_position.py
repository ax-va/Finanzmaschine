from typing import TypeVar, Generic

from finanzmaschine_core.portfolio.assets.security import Security
from finanzmaschine_core.portfolio.lots.security_lot import SecurityLot
from finanzmaschine_core.portfolio.operation_types.non_trade_increase_type import NonTradeIncreaseType
from finanzmaschine_core.portfolio.positions.acquisition_position import AcquisitionPosition
from finanzmaschine_core.portfolio.records.non_trade_decrease_record import NonTradeDecreaseRecord
from finanzmaschine_core.portfolio.records.non_trade_increase_record import NonTradeIncreaseRecord
from finanzmaschine_core.portfolio.records.security_trade_record import SecurityTradeRecord

S = TypeVar("S", bound=Security)
D = TypeVar("D", bound=NonTradeDecreaseRecord)
I = TypeVar("I", bound=NonTradeIncreaseRecord)
T = TypeVar("T", bound=SecurityTradeRecord)
L = TypeVar("L", bound=SecurityLot)

RecordIn = NonTradeIncreaseRecord | SecurityTradeRecord


class SecurityPosition(
    AcquisitionPosition[S, NonTradeDecreaseRecord, NonTradeIncreaseRecord[S, NonTradeIncreaseType], T, L],
    Generic[S, T, L],
):
    def _create_lot(self, record_in: RecordIn) -> SecurityLot:
        return SecurityLot(base_asset=self.base_asset, record_in=record_in)
