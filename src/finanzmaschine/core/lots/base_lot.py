from datetime import datetime
from math import fsum
from typing import Tuple, List

from finanzmaschine.core.assets.base_asset import BaseAsset
from finanzmaschine.core.lot_records.base_lot_record import BaseLotRecord
from finanzmaschine.utils.float_helper import round_to_zero, is_zero


class BaseLot[A: BaseAsset, R: BaseLotRecord]:
    """
    Base lot manages immutable lot records and its invariant is the quantity in the lot.

    The open quantity is derived from the incoming quantity and all outgoing quantity:

    quantity_open = quantity_in - quantity_closed.
    """

    def __init__(self, base_asset: A, record_in: R):
        self._base_asset: A = base_asset
        self._record_in: R = record_in
        self._records_out: List[R] = []

    @property
    def base_asset(self) -> A:
        return self._base_asset

    @property
    def record_in(self) -> R:
        return self._record_in

    @property
    def records_out(self) -> Tuple[R, ...]:
        return tuple(self._records_out)

    @property
    def records(self) -> Tuple[R, ...]:
        return (self._record_in, ) + self.records_out

    @property
    def last_record(self) -> R:
        return self._record_in if not self._records_out else self._records_out[-1]

    @property
    def quantity_closed(self) -> float:
        return fsum(r_out.quantity for r_out in self._records_out)

    @property
    def quantity_open(self) -> float:
        return round_to_zero(self._record_in.quantity - self.quantity_closed)

    @property
    def is_open(self) -> bool:
        return self.quantity_open > 0

    @property
    def is_closed(self) -> bool:
        return not self.is_open

    def close_record(self, record_out: R) -> R | None:
        if self.is_closed:
            raise ValueError("Lot already closed")

        if not self.can_close_by_datetime(record_out):
            raise ValueError("Records must be in ascending order by date and time")

        record_left: R | None = None
        quantity_left: float = self.quantity_open - record_out.quantity
        if quantity_left < 0 and not is_zero(quantity_left):
            record_left: R = record_out.copy(quantity=abs(quantity_left))
            record_out: R = record_out.copy(quantity=self.quantity_open)

        self._records_out.append(record_out)

        return record_left

    def can_close_by_datetime(self, record_out: R) -> bool:
        last_dt: datetime = self.last_record.dt
        return last_dt <= record_out.dt
