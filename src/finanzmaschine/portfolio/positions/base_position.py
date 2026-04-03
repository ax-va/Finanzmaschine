from abc import ABC
from collections import deque
from datetime import datetime
from enum import StrEnum
from typing import Deque, List, Tuple, TypeVar, Dict
from uuid import UUID, uuid4

from finanzmaschine.portfolio.assets.base_asset import BaseAsset
from finanzmaschine.portfolio.lots.base_lot import BaseLot
from finanzmaschine.portfolio.records.base_record import BaseRecord
from finanzmaschine.utils.float_helper import safe_sum

lot_to_position_mapping: Dict[UUID, UUID] = {}

A = TypeVar("A", bound=BaseAsset)
R = TypeVar("R", bound=BaseRecord)
L = TypeVar("L", bound=BaseLot)


class IoOrder(StrEnum):
    FIFO = "FIFO"
    LIFO = "LIFO"


class BasePosition[A, R, L](ABC):
    def __init__(self):
        self._id: UUID = uuid4()
        self._lots_open: Deque[L] = deque()
        self._lots_closed: List[L] = []

    @property
    def contains_open_lots(self) -> bool:
        return True if self._lots_open else False

    @property
    def contains_closed_lots(self) -> bool:
        return True if self._lots_closed else False

    @property
    def contains_lots(self) -> bool:
        return self.contains_open_lots or self.contains_closed_lots

    @property
    def base_asset(self) -> A:
        if not self.contains_lots:
            raise ValueError("Position doesn't contain any lot")

        lot_0: L = self._lots_open[0] if self._lots_open else self._lots_closed[0]

        return lot_0.base_asset

    @property
    def lots_open(self) -> Tuple[L, ...]:
        return tuple(self._lots_open)
    
    @property
    def lots_open_with_records_out(self) -> Tuple[L, ...]:
        return tuple(self._lots_open_with_records_out)

    @property
    def lots_closed(self) -> Tuple[L, ...]:
        return tuple(self._lots_closed)

    @property
    def first_open_lot(self) -> L:
        self.check_contains_open_lots()
        return self._lots_open[0]

    @property
    def last_open_lot(self) -> L:
        self.check_contains_open_lots()
        return self._lots_open[-1]

    @property
    def quantity_open(self) -> float:
        return safe_sum(lot.quantity_open for lot in self._lots_open)

    @property
    def quantity_closed(self) -> float:
        return safe_sum(lot.quantity_closed for lot in self._lots_closed + self._lots_open_with_records_out)

    @property
    def _lots_open_with_records_out(self) -> List[L]:
        lots: List[L] = []
        if self.first_open_lot.records_out:
            lots.append(self.first_open_lot)

        if self.first_open_lot is not self.last_open_lot and self.last_open_lot.records_out:
            lots.append(self.last_open_lot)

        return lots

    def check_contains_open_lots(self) -> None:
        if not self.contains_open_lots:
            raise ValueError("There are no open lots in the position")

    def add_lot(self, lot: L) -> None:
        if self.base_asset != lot.base_asset:
            raise ValueError(f"The position's asset must be equal to the incoming lot's asset")

        last_dt: datetime = self.last_open_lot.record_in.datetime
        if last_dt > lot.record_in.datetime:
            raise ValueError("Open lots in the position must be in ascending order by date and time")

        if lot.records_out:
            raise ValueError("Lots-in must not contain reports-out")

        if lot.id in lot_to_position_mapping:
            raise ValueError(
                f"Lot with id {lot.id!r} already mapped to "
                f"position with id {lot_to_position_mapping[lot.id]!r}"
            )
        else:
            lot_to_position_mapping[lot.id] = self._id

        self._lots_open.append(lot)

    def close_record_in_fifo_order(self, record_out: R) -> None:
        self._close_record(
            record_out=record_out,
            io_order=IoOrder.FIFO,
        )

    def close_record_in_lifo_order(self, record_out: R) -> None:
        self._close_record(
            record_out=record_out,
            io_order=IoOrder.LIFO,
        )

    def _close_record(self, record_out: R, io_order: IoOrder) -> None:
        lot_out: L = self.first_open_lot if io_order == IoOrder.FIFO else self.last_open_lot
        record_left: R | None = lot_out.close_record(record_out)
        if lot_out.is_closed:
            self._lots_closed.append(lot_out)
            self._lots_open.popleft() if io_order == IoOrder.FIFO else self._lots_open.pop()
            if record_left:
                self._close_record(
                    record_out=record_left,
                    io_order=io_order,
                )
