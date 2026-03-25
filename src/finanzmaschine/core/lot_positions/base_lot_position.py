from collections import deque
from enum import StrEnum
from typing import Deque, List, Tuple, TypeVar

from finanzmaschine.core.assets.base_asset import BaseAsset
from finanzmaschine.core.lots.base_lot import BaseLot
from finanzmaschine.core.lots.base_lot_record import BaseLotRecord

A = TypeVar("A", bound=BaseAsset)
R = TypeVar("R", bound=BaseLotRecord)
L = TypeVar("L", bound=BaseLot)


class FirstOrLast(StrEnum):
    FIRST = "first"
    LAST = "last"


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
            raise ValueError("Position doesn't contain any lot")

    @property
    def lots_open(self) -> Tuple[L, ...]:
        return tuple(self._lots_open)

    @property
    def lots_closed(self) -> Tuple[L, ...]:
        return tuple(self._lots_closed)

    @property
    def first_open(self) -> L:
        if not self._lots_open:
            raise ValueError("There are no open lots in the position")
        return self._lots_open[0]

    @property
    def last_open(self) -> L:
        if not self._lots_open:
            raise ValueError("There are no open lots in the position")
        return self._lots_open[-1]

    def add(self, lot_in: L) -> None:
        if self.base_asset != lot_in.base_asset:
            raise ValueError(f"Position's asset must be equal to incoming lot's asset")

        if self._lots_open:
            last_dt = self._lots_open[-1].record_in.dt
            if last_dt > lot_in.record_in.dt:
                raise ValueError("Open lots in the position must be in ascending order by date and time")

        if lot_in.records_out:
            raise ValueError("Incoming lot must not have outgoing reports")

        self._lots_open.append(lot_in)

    def close_record(self, record_out: R, in_which_lot: str) -> None:
        lot: L = self._get_open_lot(in_which_lot)
        record_left: R | None = lot.close_record(record_out)
        if record_left:
            closed_lot: L = self._lots_open.popleft() if in_which_lot == "first" else self._lots_open.pop()
            self._lots_closed.append(closed_lot)
            self.close_record(
                record_out=record_left,
                in_which_lot=in_which_lot,
            )

    def _get_open_lot(self, which_lot: str) -> L:
        if which_lot not in (FirstOrLast.FIRST, FirstOrLast.LAST):
            raise ValueError("The `which_lot` parameter must be either 'first' or 'last'")
        lot: L = self.first_open if which_lot == FirstOrLast.FIRST else self.last_open
        return  lot
