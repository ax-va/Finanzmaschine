from datetime import datetime
from decimal import Decimal
from typing import override

from finanzmaschine.core.lots.base_lot import BaseLot
from finanzmaschine.utils.float_helper import round_to_zero


class NominalLot(BaseLot):
    """
    A lot whose invariant is the number of nominal units.

    The open units are derived from the incoming units and all outgoing units:
    units_open = units_in - units_closed.
    """

    @property
    def units_open(self) -> float:
        return round_to_zero(self.lot_record_in.units - self.units_closed)

    @property
    def is_open(self) -> bool:
        return self.units_open > 0

    @property
    def is_closed(self) -> bool:
        return not self.is_open

    @override
    def _validate_record_out(
        self,
        units: float,
        price: Decimal,
        fee: Decimal,
        dt: datetime,
    ) -> None:
        super()._validate_record_out(units, price, fee, dt)
        assert round_to_zero(self.units_open - units) >= 0
