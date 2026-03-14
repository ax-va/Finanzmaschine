from datetime import datetime
from typing import Tuple

from finanzmaschine.core.lots.lot_record import LotRecord
from finanzmaschine.core.lots.lot_state import LotState


class BaseLot:
    """
    Base lot managing immutable lot records.
    """

    def __init__(self):
        self.state = LotState.NEW
        self.lot_record_in: LotRecord | None = None
        self.lot_records_out: Tuple[LotRecord, ...] = ()
        self._units_out_total: float = 0.0

    @property
    def units_out_total(self) -> float:
        return self._units_out_total

    def record_in(
        self,
        *,
        units: float,
        price: float,
        fee: float,
        dt: datetime,
    ) -> None:
        assert self.state == LotState.NEW, "Lot already opened"
        assert units > 0
        assert price > 0
        assert fee >= 0

        self.lot_record_in = LotRecord(
            units=units,
            price=price,
            fee=fee,
            dt=dt,
        )

    def record_out(
        self,
        *,
        units: float,
        price: float,
        fee: float,
        dt: datetime,
    ) -> None:
        assert self.state == LotState.OPEN, "Lot not open"
        assert self.lot_record_in.units > 0
        assert units > 0
        assert price > 0
        assert fee >= 0

        lot_record_out = LotRecord(
            units=units,
            price=price,
            fee=fee,
            dt=dt,
        )
        self.lot_records_out = *self.lot_records_out, lot_record_out
        self._units_out_total += units
