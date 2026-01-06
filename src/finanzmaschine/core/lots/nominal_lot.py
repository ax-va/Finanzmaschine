import datetime as dt
from typing import override

from finanzmaschine.core.lots.base_lot import BaseLot, TLotRecord
from finanzmaschine.core.lots.base_lot_record import BaseLotRecord


class NominalLot(BaseLot[TLotRecord]):
    """
    A lot that represents a lot with an invariant unit balance.

    The number of units is invariant: units_open = units_in - units_out_total.
    """

    record_cls = BaseLotRecord

    @property
    def units_open(self) -> float:
        return self.lot_record_in.units - self.units_out_total

    @property
    def is_open(self) -> bool:
        return self.units_open > 0

    @property
    def is_closed(self) -> bool:
        return not self.is_open

    @override
    def record_out(
        self,
        *,
        units: float,
        price: float,
        datetime: dt.datetime,
        **kwargs,
    ) -> None:
        assert units <= self.units_open
        return super().record_out(
            units=units,
            price=price,
            datetime=datetime,
            **kwargs,
        )
