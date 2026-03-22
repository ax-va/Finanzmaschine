from collections import deque
from typing import Generic

from finanzmaschine.core.assets.asset import A
from finanzmaschine.core.lots.base_lot import L
from finanzmaschine.core.lots.base_lot_record import R


class Position(Generic[A]):
    def __init__(self):
        self.lots_open = deque()
        self.lots_closed = deque()

    @property
    def base_asset(self) -> A | None:
        if self.lots_open:
            return self.lots_open[0].base_asset

        elif self.lots_closed:
            return self.lots_closed[0].base_asset

        else:
            return None

    def add_lot(self, lot_in: L) -> None:
        if self.base_asset is not None and self.base_asset != lot_in.base_asset:
            raise ValueError("The position's base asset is not equal to the incoming lot's base asset")

        # datetime

        self.lots_open.append(lot_in)

    def close_record(self, record_out: R) -> None:
        lot = self.lots_open[0]
        ...
