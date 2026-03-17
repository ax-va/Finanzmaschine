from math import fsum
from typing import Tuple, Any, TypeVar, Generic

from finanzmaschine.core.lots.base_lot_record import BaseLotRecord
from finanzmaschine.utils.float_helper import round_to_zero, is_zero

R = TypeVar("R", bound="BaseLotRecord")


class BaseLot(Generic[R]):
    """
    Base lot manages immutable lot records and its invariant is the base asset quantity.

    The open quantity is derived from the incoming quantity and all outgoing quantity:

    quantity_open = quantity_in - quantity_closed.
    """

    def __init__(self, base_asset: Any, record_in: R):
        self.base_asset: Any = base_asset
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

    def close_quantity(self, record_out: R) -> None:
        self._ensure_can_close(record_out)
        self.records_out = self.records_out + (record_out, )

    def _ensure_can_close(self, record_out: R) -> None:
        remaining_quantity = self.quantity_open - record_out.quantity
        if remaining_quantity < 0 and not is_zero(remaining_quantity):
            raise ValueError("Cannot close more than open quantity")

        last_dt = self.last_record.dt
        if not (last_dt < record_out.dt):
            raise ValueError("Records must be strictly increasing ordered by datetime")

