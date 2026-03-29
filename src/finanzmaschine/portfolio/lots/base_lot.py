import math

from datetime import datetime
from typing import Tuple, List, TypeVar

from finanzmaschine.portfolio.assets import BaseAsset
from finanzmaschine.portfolio.records.base_record import Direction
from finanzmaschine.portfolio.records.non_sale_reduction_record import NonSaleReductionRecord
from finanzmaschine.portfolio.records.priced_record import PricedRecord
from finanzmaschine.utils.float_helper import round_to_zero, is_zero

A = TypeVar("A", bound=BaseAsset)
N = TypeVar("N", bound=NonSaleReductionRecord)
P = TypeVar("P", bound=PricedRecord)


class BaseLot[A, N, P]:
    """
    Base lot manages immutable lot records.

    Its invariant is the quantity in the lot.
    The open quantity is derived from the incoming quantity and all outgoing quantity:

    quantity_open = quantity_in - quantity_closed.
    """

    def __init__(self, base_asset: A, record_in: P):
        self._base_asset: A = base_asset

        if record_in.direction is None:
            record_in: P = record_in.copy(direction=Direction.IN)
        elif record_in.direction != Direction.IN:
            raise ValueError(f"Direction of the record-in must be {Direction.IN!r}")

        self._records: List[N | P] = [record_in]

    @property
    def base_asset(self) -> A:
        return self._base_asset

    @property
    def records(self) -> Tuple[N | P, ...]:
        return tuple(self._records)

    @property
    def record_in(self) -> P:
        return self._records[0]

    @property
    def records_out(self) -> Tuple[N | P, ...]:
        return tuple(self._records[1:])

    @property
    def last_record(self) -> N | P:
        return self._records[-1]

    @property
    def quantity_closed(self) -> float:
        return math.fsum(r_out.quantity for r_out in self._records[1:])

    @property
    def quantity_open(self) -> float:
        return round_to_zero(self._records[0].quantity - self.quantity_closed)

    @property
    def is_open(self) -> bool:
        return self.quantity_open > 0

    @property
    def is_closed(self) -> bool:
        return not self.is_open

    @property
    def unit_cost_basis(self) -> float:
        return (self.record_in.gross_value + self.record_in.fee) / self.record_in.quantity

    def close_record(self, record_out: N | P) -> N | P | None:
        if self.is_closed:
            raise ValueError("Lot already closed")

        if record_out.direction is None:
            record_out: N | P = record_out.copy(direction=Direction.OUT)
        elif record_out.direction != Direction.OUT:
            raise ValueError(f"Direction of records-out must be {Direction.OUT!r}")

        if not self.can_close_by_datetime(record_out):
            raise ValueError("Records must be in ascending order by date and time")

        record_left: N | P | None = None
        quantity_left: float = self.quantity_open - record_out.quantity
        if quantity_left < 0 and not is_zero(quantity_left):
            record_left: N | P = record_out.copy(quantity=abs(quantity_left))
            record_out: N | P = record_out.copy(quantity=self.quantity_open)

        self._records.append(record_out)

        return record_left

    def can_close_by_datetime(self, record_out: N | P) -> bool:
        last_dt: datetime = self.last_record.dt
        return last_dt <= record_out.dt
