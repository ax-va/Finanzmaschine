from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from types import MappingProxyType
from typing import Tuple, Dict

from finanzmaschine_core.portfolio.assets.base_asset import BaseAsset
from finanzmaschine_core.portfolio.lots.base_lot import BaseLot
from finanzmaschine_core.portfolio.operations.direction_enum import DirectionEnum
from finanzmaschine_core.portfolio.records.base_record import BaseRecord
from finanzmaschine_core.helpers.decimal_helper import safe_sum


class ClosingOrder(StrEnum):
    FIFO = "FIFO"
    LIFO = "LIFO"


class BasePosition[A: BaseAsset, RI: BaseRecord, RO: BaseRecord, L: BaseLot](ABC):
    def __init__(self, base_asset: A):
        self._base_asset: A = base_asset
        self._closing_order: ClosingOrder | None = None
        self._closing_order_by_record_out: Dict[RO, ClosingOrder] = {}
        self._lot_by_record_out: Dict[RO, L] = {}
        self._index_by_lot: Dict[L, int] = {}

    @property
    def closing_order(self) -> ClosingOrder:
        if self._closing_order is None:
            raise ValueError("Closing order not specified")
        return self._closing_order

    @closing_order.setter
    def closing_order(self, closing_order: ClosingOrder) -> None:
        self._closing_order = closing_order

    @property
    def closing_order_by_record_out(self) -> MappingProxyType[RO, ClosingOrder]:
        return MappingProxyType(self._closing_order_by_record_out)

    @property
    def lot_by_record_out(self) -> MappingProxyType[RO, L]:
        return MappingProxyType(self._lot_by_record_out)

    @property
    def index_by_lot(self) -> MappingProxyType[L, int]:
        return MappingProxyType(self._index_by_lot)

    @property
    def lots(self) -> Tuple[L, ...]:
        return tuple(lot for lot in self._index_by_lot)

    @property
    def lots_open(self) -> Tuple[L, ...]:
        return tuple(lot for lot in self._index_by_lot if lot.is_open)

    @property
    def lots_fully_closed(self) -> Tuple[L, ...]:
        return tuple(lot for lot in self._lots_with_records_out if lot.is_closed)

    @property
    def lots_partially_closed(self) -> Tuple[L, ...]:
        return tuple(lot for lot in self._lots_with_records_out if lot.is_open)

    @property
    def contains_lots(self) -> bool:
        return True if self._index_by_lot else False

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
        # workaround for type checker
        lot: BaseLot
        return safe_sum(lot.quantity_open for lot in self.lots_open)

    @property
    def quantity_closed(self) -> Decimal:
        return safe_sum(r_out.quantity for r_out in self._closing_order_by_record_out)

    @property
    def _lots_with_records_out(self) -> Tuple[L, ...]:
        return tuple(dict.fromkeys(self._lot_by_record_out.values()))

    @abstractmethod
    def _create_lot(self, record_in: RI) -> L:
        pass

    def get_lot_id(self, lot: L) -> str:
        num_lots = len(self._index_by_lot)
        num_zeros = len(str(num_lots))
        lot_index = self._index_by_lot[lot]
        lot_id = f"LOT_{lot_index + 1:0{num_zeros}d}"
        return lot_id

    def set_closing_order(self, value: str) -> None:
        self._closing_order = ClosingOrder(value.upper())

    def apply(self, record: RI | RO) -> None:
        if record.operation.variant.direction == DirectionEnum.IN:
            lot = self._create_lot(record_in=record)
            self._append(lot)
        elif record.operation.variant.direction == DirectionEnum.OUT:
            self._reduce(
                record_out=record,
                closing_order=self.closing_order,
            )
        else:
            raise ValueError(
                f"Direction is neither {DirectionEnum.IN!r} nor {DirectionEnum.OUT!r}: {record.operation.variant.direction}"
            )

    def _append(self, lot: L) -> None:
        if self.base_asset != lot.base_asset:
            raise ValueError(f"The position's base asset must be equal to the lot's base asset")

        if self.contains_open_lots:
            last_dt: datetime = self.last_open_lot.record_in.datetime
            if last_dt > lot.record_in.datetime:
                raise ValueError("Open lots in the position must be in ascending order by date and time")

        if lot.records_out:
            raise ValueError("New lots must not contain reports-out")

        self._index_by_lot[lot] = len(self._index_by_lot)

    def _reduce(self, record_out: RO, closing_order: ClosingOrder) -> None:
        if closing_order == ClosingOrder.FIFO:
            lot = self.first_open_lot
        elif closing_order == ClosingOrder.LIFO:
            lot = self.last_open_lot
        else:
            raise ValueError(f"Closing order is neither {ClosingOrder.FIFO} nor {ClosingOrder.LIFO}")

        split: Tuple[RO, RO] | None = lot.reduce(record_out)

        if not split:
            self._closing_order_by_record_out[record_out] = closing_order
            self._lot_by_record_out[record_out] = lot
        else:
            record_closing: RO = split[0]
            self._closing_order_by_record_out[record_closing] = closing_order
            self._lot_by_record_out[record_closing] = lot
            record_remaining: RO = split[1]
            self._reduce(record_remaining, closing_order)
