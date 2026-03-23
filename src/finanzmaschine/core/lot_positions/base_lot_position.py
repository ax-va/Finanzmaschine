from collections import deque
from typing import Deque, List, Tuple, TypeVar

from finanzmaschine.core.assets.base_asset import BaseAsset
from finanzmaschine.core.lots.base_lot import BaseLot
from finanzmaschine.core.lots.base_lot_record import BaseLotRecord

A = TypeVar("A", bound=BaseAsset)
R = TypeVar("R", bound=BaseLotRecord)
L = TypeVar("L", bound=BaseLot)


class BaseLotPosition[A, R, L]:
    def __init__(self):
        self._lots_open: Deque[L] = deque()
        self._lots_closed: List[L] = []

    @property
    def base_asset(self) -> A:
        if self._lots_open:
            return self._lots_open[0].base_asset
        elif self._lots_closed:
            return self._lots_closed[0].base_asset
        else:
            raise ValueError("The position doesn't contain any lot")

    @property
    def lots_open(self) -> Tuple[L, ...]:
        return tuple(self._lots_open)

    @property
    def lots_closed(self) -> Tuple[L, ...]:
        return tuple(self._lots_closed)

    def open_lot(self, lot_in: L) -> None:
        asset = self.base_asset
        if asset != lot_in.base_asset:
            raise ValueError(
                f"The position's asset {asset!r} is not equal to the incoming lot's asset {lot_in.base_asset!r}"
            )

        last_dt = self._lots_open[-1].record_in.dt
        if last_dt > lot_in.record_in.dt:
            raise ValueError("Open lots in the position must be in ascending order by date and time")

        if lot_in.records_out:
            raise ValueError("The incoming lot must not have outgoing reports")

        self._lots_open.append(lot_in)

    def close_record(self, record_out: R, in_which_lot: str) -> None:
        if in_which_lot == "first":
            lot = self._lots_open[0]
        elif in_which_lot == "last":
            lot = self._lots_open[-1]
        else:
            raise ValueError("The value of `in_which_lot` must be either 'first' or 'last'")
