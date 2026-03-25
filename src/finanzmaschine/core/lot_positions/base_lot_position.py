import math
from collections import deque
from enum import StrEnum
from typing import Deque, List, Tuple, TypeVar

from finanzmaschine.core.assets.base_asset import BaseAsset
from finanzmaschine.core.lots.base_lot import BaseLot
from finanzmaschine.core.lots.base_lot_record import BaseLotRecord

A = TypeVar("A", bound=BaseAsset)
R = TypeVar("R", bound=BaseLotRecord)
L = TypeVar("L", bound=BaseLot)


class IoOrder(StrEnum):
    FIFO = "FIFO"
    LIFO = "LIFO"


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

    @property
    def quantity_open(self) -> float:
        return math.fsum(lot.quantity_open for lot in self._lots_open)

    @property
    def quantity_closed(self) -> float:
        lots: List[L] = (
            [self.first_open, self.last_open]
            if id(self.first_open) != id(self.last_open)
            else [self.first_open]
        )
        lots = self._lots_closed + lots
        return math.fsum(lot.quantity_closed for lot in lots)

    @property
    def price_average_open(self) -> float:
        return math.fsum(lot.quantity_open * lot.record_in.price for lot in self._lots_open) / self.quantity_open

    def add_open_lot(self, lot_in: L) -> None:
        if self.base_asset != lot_in.base_asset:
            raise ValueError(f"Position's asset must be equal to incoming lot's asset")

        if self._lots_open:
            last_dt = self._lots_open[-1].record_in.dt
            if last_dt > lot_in.record_in.dt:
                raise ValueError("Open lots in the position must be in ascending order by date and time")

        if lot_in.records_out:
            raise ValueError("Incoming lot must not have outgoing reports")

        self._lots_open.append(lot_in)

    def close_record(self, record_out: R, io_order: IoOrder) -> None:
        lot_out: L = self.first_open if io_order == IoOrder.FIFO else self.last_open
        record_left: R | None = lot_out.close_record(record_out)
        if record_left:
            closed_lot: L = self._lots_open.popleft() if io_order == IoOrder.FIFO else self._lots_open.pop()
            self._lots_closed.append(closed_lot)
            self.close_record(
                record_out=record_left,
                io_order=io_order,
            )
