from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from types import MappingProxyType
from typing import Deque, List, Tuple, TypeVar, Dict

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
        self._closing_order: ClosingOrder | None = None
        self._closing_orders: Dict[R, ClosingOrder] = {}
        self._record_out_lots: Dict[R, L] = {}
        self._lot_indices: Dict[L, int] = {}

    @property
    def closing_order(self) -> ClosingOrder:
        if self._closing_order is None:
            raise ValueError("Closing order not specified")
        return self._closing_order

    @closing_order.setter
    def closing_order(self, closing_order: ClosingOrder) -> None:
        self._closing_order = closing_order

    @property
    def closing_orders(self) -> MappingProxyType[R, ClosingOrder]:
        return MappingProxyType(self._closing_orders)

    @property
    def record_out_lots(self) -> MappingProxyType[R, L]:
        return MappingProxyType(self._record_out_lots)

    @property
    def lot_indices(self) -> MappingProxyType[L, int]:
        return MappingProxyType(self._lot_indices)

    @property
    def lots(self) -> Tuple[L, ...]:
        return tuple(lot for lot in self._lot_indices)

    @property
    def lots_open(self) -> Tuple[L, ...]:
        return tuple(lot for lot in self._lot_indices if lot.is_open)

    @property
    def lots_fully_closed(self) -> Tuple[L, ...]:
        return tuple(lot for lot in self._lots_with_records_out if lot.is_closed)

    @property
    def contains_lots(self) -> bool:
        return True if self._lot_indices else False

    @property
    def contains_open_lots(self) -> bool:
        return True if self.lots_open else False

    @property
    def base_asset(self) -> A:
        return self._base_asset

    @property
    def first_open_lot(self) -> L:
        lots_open = self.lots_open
        if not lots_open:
            raise ValueError("There are no open lots in the position")
        return lots_open[0]

    @property
    def last_open_lot(self) -> L:
        lots_open = self.lots_open
        if not lots_open:
            raise ValueError("There are no open lots in the position")
        return lots_open[-1]

    @property
    def quantity_open(self) -> Decimal:
        return safe_sum(lot.quantity_open for lot in self.lots_open)

    @property
    def quantity_closed(self) -> Decimal:
        return safe_sum(r_out.quantity for r_out in self._closing_orders)
        # return safe_sum(lot.quantity_closed for lot in self.lots_with_records_out)

    @abstractmethod
    def _create_lot(self, record_in: R) -> L:
        pass

    @property
    def _lots_with_records_out(self) -> List[L]:
        return [lot for lot in self._lot_indices if lot.records_out]

    def get_lot_id(self, lot: L) -> str:
        num_lots = len(self._lot_indices)
        num_zeros = len(str(num_lots))
        lot_index = self._lot_indices[lot]
        lot_id = f"LOT_{lot_index + 1:0{num_zeros}d}"
        return lot_id

    def set_closing_order(self, value: str) -> None:
        self._closing_order = ClosingOrder(value.upper())

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

        self._lot_indices[lot] = len(self._lot_indices)

    def _reduce(self, record_out: R, closing_order: ClosingOrder) -> None:

        lot: L
        if closing_order == ClosingOrder.FIFO:
            lot = self.first_open_lot
        elif closing_order == ClosingOrder.LIFO:
            lot = self.last_open_lot
        else:
            raise ValueError(f"Closing order is neither {ClosingOrder.FIFO} nor {ClosingOrder.LIFO}")

        split: Tuple[R, R] | None = lot.reduce(record_out)

        if not split:
            self._closing_orders[record_out] = closing_order
            self._record_out_lots[record_out] = lot
        else:
            record_closing: R = split[0]
            self._closing_orders[record_closing] = closing_order
            self._record_out_lots[record_closing] = lot
            record_remaining: R = split[1]
            self._reduce(record_remaining, closing_order)
