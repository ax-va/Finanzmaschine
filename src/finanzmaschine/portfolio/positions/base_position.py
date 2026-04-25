from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Deque, List, Tuple, TypeVar

from finanzmaschine.portfolio.assets.base_asset import BaseAsset
from finanzmaschine.portfolio.lots.base_lot import BaseLot
from finanzmaschine.portfolio.records.base_record import BaseRecord, Direction
from finanzmaschine.utils.decimal_helper import safe_sum

A = TypeVar("A", bound=BaseAsset)
R = TypeVar("R", bound=BaseRecord)
L = TypeVar("L", bound=BaseLot)


class ClosingOrder(StrEnum):
    FIFO = "FIFO"
    LIFO = "LIFO"


class BasePosition[A, R, L](ABC):
    def __init__(self, base_asset: A):
        self._base_asset: A = base_asset
        self._lots_open: Deque[L] = deque()
        self._lots_fully_closed: List[L] = []
        self._closing_order: ClosingOrder | None = None

    @property
    def closing_order(self) -> ClosingOrder:
        if self._closing_order is None:
            raise ValueError("Closing order not specified")
        return self._closing_order

    @closing_order.setter
    def closing_order(self, closing_order: ClosingOrder) -> None:
        self._closing_order = closing_order

    @property
    def contains_open_lots(self) -> bool:
        return True if self._lots_open else False

    @property
    def contains_fully_closed_lots(self) -> bool:
        return True if self._lots_fully_closed else False

    @property
    def contains_lots(self) -> bool:
        return self.contains_open_lots or self.contains_fully_closed_lots

    @property
    def base_asset(self) -> A:
        return self._base_asset

    @property
    def lots_open(self) -> Tuple[L, ...]:
        return tuple(self._lots_open)
    
    @property
    def lots_partially_closed(self) -> Tuple[L, ...]:
        return tuple(self._lots_partially_closed)

    @property
    def lots_fully_closed(self) -> Tuple[L, ...]:
        return tuple(self._lots_fully_closed)

    @property
    def lots_with_records_out(self) -> Tuple[L, ...]:
        return tuple(self._lots_with_records_out)

    @property
    def first_open_lot(self) -> L:
        self.ensure_contains_open_lots()
        return self._lots_open[0]

    @property
    def last_open_lot(self) -> L:
        self.ensure_contains_open_lots()
        return self._lots_open[-1]

    @property
    def quantity_open(self) -> Decimal:
        return safe_sum(lot.quantity_open for lot in self._lots_open)

    @property
    def quantity_closed(self) -> Decimal:
        return safe_sum(lot.quantity_closed for lot in self._lots_with_records_out)

    @property
    def _lots_partially_closed(self) -> List[L]:
        lots: List[L] = []
        if self.first_open_lot.records_out:
            lots.append(self.first_open_lot)

        if self.first_open_lot is not self.last_open_lot and self.last_open_lot.records_out:
            lots.append(self.last_open_lot)

        return lots

    @property
    def _lots_with_records_out(self) -> List[L]:
        return self._lots_fully_closed + self._lots_partially_closed

    @abstractmethod
    def _create_lot(self, record_in: R) -> L:
        pass

    def ensure_contains_open_lots(self) -> None:
        if not self.contains_open_lots:
            raise ValueError("There are no open lots in the position")

    def apply(self, record: R) -> None:
        if record.direction == Direction.IN:
            lot = self._create_lot(record_in=record)
            self._append(lot)
        elif record.direction == Direction.OUT:
            self._reduce(
                record_out=record,
                closing_order=self.closing_order,
            )
        else:
            raise ValueError(f"Direction is neither {Direction.IN} nor {Direction.OUT}: {record.direction}")

    def _append(self, lot: L) -> None:
        if self.base_asset != lot.base_asset:
            raise ValueError(f"The position's asset must be equal to the incoming lot's asset")

        if self.contains_open_lots:
            last_dt: datetime = self.last_open_lot.record_in.datetime
            if last_dt > lot.record_in.datetime:
                raise ValueError("Open lots in the position must be in ascending order by date and time")

        if lot.records_out:
            raise ValueError("Lots-in must not contain reports-out")

        self._lots_open.append(lot)

    def _reduce(self, record_out: R, closing_order: ClosingOrder) -> None:
        self.ensure_contains_open_lots()

        lot: L
        if closing_order == ClosingOrder.FIFO:
            lot = self.first_open_lot
        elif closing_order == ClosingOrder.LIFO:
            lot = self.last_open_lot
        else:
            raise ValueError(f"Closing order is neither {ClosingOrder.FIFO} nor {ClosingOrder.LIFO}")

        record_remaining: R | None = lot.reduce(record_out)
        if lot.is_closed:
            self._lots_fully_closed.append(lot)
            self._lots_open.popleft() if closing_order == ClosingOrder.FIFO else self._lots_open.pop()
            if record_remaining:
                self._reduce(record_remaining, closing_order)
