import math
from collections import deque
from datetime import datetime
from enum import StrEnum
from typing import Deque, List, Tuple, TypeVar

from finanzmaschine.core.assets.base_asset import BaseAsset
from finanzmaschine.core.lots.base_lot import BaseLot
from finanzmaschine.core.lot_records.base_lot_record import BaseLotRecord

A = TypeVar("A", bound=BaseAsset)
R = TypeVar("R", bound=BaseLotRecord)
L = TypeVar("L", bound=BaseLot)


class IoOrder(StrEnum):
    FIFO = "FIFO"
    LIFO = "LIFO"


class BasePosition[A, R, L]:
    def __init__(self):
        self._lots_open: Deque[L] = deque()
        self._lots_closed: List[L] = []

    @property
    def base_asset(self) -> A:
        if not self.contains_lots():
            raise ValueError("Position doesn't contain any lot")

        lot_0: L = self._lots_open[0] if self._lots_open else self._lots_closed[0]

        return lot_0.base_asset

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
        lot_list: List[L] = []
        if self.first_open.records_out:
            lot_list.append(self.first_open)

        if self.first_open is not self.last_open and self.last_open.records_out:
            lot_list.append(self.last_open)

        return math.fsum(lot.quantity_closed for lot in self._lots_closed + lot_list)

    @property
    def price_average_open(self) -> float:
        # TODO: different quote assets -> Dict[BaseAsset, float]
        return math.fsum(lot.quantity_open * lot.record_in.price for lot in self._lots_open) / self.quantity_open

    def contains_lots(self) -> bool:
        return True if self._lots_open or self._lots_closed else False

    def add_lot(self, lot_in: L) -> None:
        if self.base_asset != lot_in.base_asset:
            raise ValueError(f"Position's asset must be equal to incoming lot's asset")

        last_dt: datetime = self.last_open.record_in.dt
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
