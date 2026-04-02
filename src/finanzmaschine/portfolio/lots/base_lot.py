from datetime import datetime
from typing import Tuple, List, TypeVar
from uuid import UUID, uuid4

from finanzmaschine.portfolio.assets import BaseAsset
from finanzmaschine.portfolio.records.base_record import Direction, BaseRecord
from finanzmaschine.utils.float_helper import round_to_zero, is_zero, safe_sum, FLOAT_EPS

A = TypeVar("A", bound=BaseAsset)
R = TypeVar("R", bound=BaseRecord)
I = TypeVar("I", bound=BaseRecord)


class BaseLot[A, R, I]:
    """
    Base lot manages immutable lot records.

    Its invariant is the quantity in the lot.
    The open quantity is derived from the incoming quantity and all outgoing quantity:

    quantity_open = quantity_in - quantity_closed.
    """

    def __init__(self, base_asset: A, record_in: I):
        self._id: UUID = uuid4()
        self._base_asset: A = base_asset

        if record_in.direction != Direction.IN:
            raise ValueError(f"Direction of the record-in must be {Direction.IN!r}")

        self._records: List[R] = [record_in]

    @property
    def base_asset(self) -> A:
        return self._base_asset

    @property
    def records(self) -> Tuple[R, ...]:
        return tuple(self._records)

    @property
    def record_in(self) -> I:
        return self._records[0]

    @property
    def records_out(self) -> Tuple[R, ...]:
        return tuple(self._records[1:])

    @property
    def last_record(self) -> R:
        return self._records[-1]

    @property
    def quantity_closed(self) -> float:
        return safe_sum(r_out.quantity for r_out in self._records[1:])

    @property
    def quantity_open(self) -> float:
        return round_to_zero((self._records[0].quantity - self.quantity_closed), float_eps=FLOAT_EPS)

    @property
    def is_open(self) -> bool:
        return self.quantity_open > 0

    @property
    def is_closed(self) -> bool:
        return not self.is_open

    def close_record(self, record_out: R) -> R | None:
        if self.is_closed:
            raise ValueError("Lot already closed")

        if record_out.direction != Direction.OUT:
            raise ValueError(f"Direction of records-out must be {Direction.OUT!r}")

        if not self.has_valid_datetime(record_out):
            raise ValueError("Records must be in ascending order by date and time")

        record_left: R | None = None
        quantity_left: float = self.quantity_open - record_out.quantity
        if quantity_left < 0 and not is_zero(quantity_left, float_eps=FLOAT_EPS):
            record_out: R = record_out.copy(
                id=uuid4(),
                quantity=self.quantity_open,
                split_from_id=record_out.id,
            )
            record_left: R = record_out.copy(
                id=uuid4(),
                quantity=abs(quantity_left),
                split_from_id=record_out.id,
            )

        self._records.append(record_out)

        return record_left

    def has_valid_datetime(self, record_out: R) -> bool:
        last_dt: datetime = self.last_record.datetime
        return last_dt <= record_out.datetime
