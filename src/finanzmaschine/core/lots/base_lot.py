from math import fsum
from typing import Tuple, Generic, TypeVar

from finanzmaschine.core.assets.asset import A
from finanzmaschine.core.lots.base_lot_record import R
from finanzmaschine.core.lots.lot_errors import ClosingMoreThanOpenQuantityError, OrderingByDatetimeError
from finanzmaschine.utils.float_helper import round_to_zero, is_zero

L = TypeVar("L", bound="BaseLot")


class BaseLot(Generic[A, R]):
    """
    Base lot manages immutable lot records and its invariant is the quantity in the lot.

    The open quantity is derived from the incoming quantity and all outgoing quantity:

    quantity_open = quantity_in - quantity_closed.
    """

    def __init__(self, base_asset: A, record_in: R):
        self.base_asset: A = base_asset
        self.record_in: R = record_in
        self.records_out: Tuple[R, ...] = ()

    @property
    def records(self) -> Tuple[R, ...]:
        return (self.record_in, ) + self.records_out

    @property
    def last_record(self) -> R:
        return self.record_in if not self.records_out else self.records_out[-1]

    @property
    def quantity_closed(self) -> float:
        return fsum(r_out.quantity for r_out in self.records_out)

    @property
    def quantity_open(self) -> float:
        return round_to_zero(self.record_in.quantity - self.quantity_closed)

    @property
    def is_open(self) -> bool:
        return self.quantity_open > 0

    @property
    def is_closed(self) -> bool:
        return not self.is_open

    def close_record(self, record_out: R) -> None:
        self.ensure_can_close(record_out)
        self.records_out = self.records_out + (record_out, )

    def can_close_by_quantity(self, record_out: R) -> bool:
        remaining_quantity = self.quantity_open - record_out.quantity
        return remaining_quantity >= 0 or is_zero(remaining_quantity)

    def can_close_by_datetime(self, record_out: R) -> bool:
        last_dt = self.last_record.dt
        return last_dt <= record_out.dt

    def ensure_can_close(self, record_out: R) -> None:
        if not self.can_close_by_quantity(record_out):
            raise ClosingMoreThanOpenQuantityError()

        if not self.can_close_by_datetime(record_out):
            raise OrderingByDatetimeError()
