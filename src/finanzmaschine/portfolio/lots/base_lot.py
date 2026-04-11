from abc import ABC
from datetime import datetime
from decimal import Decimal
from typing import Tuple, List

from finanzmaschine.portfolio.assets.base_asset import BaseAsset
from finanzmaschine.portfolio.records.base_record import Direction, BaseRecord
from finanzmaschine.utils.decimal_helper import safe_sum, round_to_zero, is_zero


class BaseLot[A: BaseAsset, R: BaseRecord, I: BaseRecord](ABC):
    """
    Abstract base class to manage lot records.

    The first record in the lot must be a record-in, which opens the lot.
    All other records must be records-out,
    which reduce the quantity of the base asset until the lot will be closed.

    The lot's invariant is the quantity of the base asset.
    The open quantity is derived from the incoming quantity and all outgoing quantity:
    quantity_open = quantity_in - quantity_closed.
    """

    def __init__(self, base_asset: A, record_in: I):
        self._base_asset: A = base_asset

        if record_in.direction != Direction.IN:
            raise ValueError(f"Direction of the record-in must always be {Direction.IN!r}")

        self._record_in: I = record_in
        self._records_out: List[R] = []

    @property
    def base_asset(self) -> A:
        return self._base_asset

    @property
    def record_in(self) -> I:
        return self._record_in

    @property
    def records_out(self) -> Tuple[R, ...]:
        return tuple(self._records_out)

    @property
    def last_record(self) -> R | I:
        return self._record_in if not self._records_out else self._records_out[-1]

    @property
    def quantity_closed(self) -> Decimal:
        return safe_sum(r_out.quantity for r_out in self._records_out)

    @property
    def quantity_open(self) -> Decimal:
        return round_to_zero(self._record_in.quantity - self.quantity_closed, self.base_asset.quantum)

    @property
    def is_open(self) -> bool:
        return self.quantity_open > Decimal("0")

    @property
    def is_closed(self) -> bool:
        return not self.is_open

    def reduce(self, record_out: R) -> R | None:
        if self.is_closed:
            raise ValueError("Lot already closed")

        if record_out.direction != Direction.OUT:
            raise ValueError(f"Direction of records-out must always be {Direction.OUT!r}")

        if not self.has_valid_datetime(record_out):
            raise ValueError("Records must be in ascending order by date and time")

        quantity_left: Decimal = self.quantity_open - record_out.quantity
        if quantity_left < Decimal("0") and not is_zero(quantity_left, self.base_asset.quantum):
            record_closing: R = record_out.copy(
                quantity=self.quantity_open,
            )
            record_left: R = record_out.copy(
                quantity=abs(quantity_left),
            )
            self._records_out.append(record_closing)
            return record_left

        self._records_out.append(record_out)
        return None

    def has_valid_datetime(self, record_out: R) -> bool:
        last_dt: datetime = self.last_record.datetime
        return last_dt <= record_out.datetime
