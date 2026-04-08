from typing import TypeVar

from finanzmaschine.portfolio.assets.etp import Etp
from finanzmaschine.portfolio.lots import EtpLot
from finanzmaschine.portfolio.positions.security_position import SecurityPosition
from finanzmaschine.portfolio.records.etp_trade_record import EtpTradeRecord
from finanzmaschine.portfolio.records.non_trade_increase_record import NonTradeIncreaseRecord

E = TypeVar("E", bound=Etp)
T = TypeVar("T", bound=EtpTradeRecord)
L = TypeVar("L", bound=EtpLot)

RecordIn = NonTradeIncreaseRecord | EtpTradeRecord


class EtpPosition(SecurityPosition[E, T, L]):

    def _create_lot(self, record_in: RecordIn) -> EtpLot:
        return EtpLot(base_asset=self.base_asset, record_in=record_in)
