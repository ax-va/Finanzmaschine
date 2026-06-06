from abc import ABC
from datetime import datetime
from decimal import Decimal
from typing import Tuple, List

from finanzmaschine_core.portfolio.assets.base_asset import BaseAsset
from finanzmaschine_core.portfolio.operations.direction_enum import DirectionEnum
from finanzmaschine_core.portfolio.records.base_record import BaseRecord
from finanzmaschine_core.helpers.decimal_helper import safe_sum, round_to_quantum, validate_precision


class BaseLot[A: BaseAsset, RI: BaseRecord, RO: BaseRecord](ABC):
    """
    Abstract base class to manage internal lot records.

    The first record in a lot must be a record-in, which opens the lot.
    All other records must be records-out,
    which reduce the quantity of the base asset until the lot will be closed.

    The lot's invariant is the quantity of the base asset.
    The open quantity is derived from the incoming quantity and all outgoing quantity:
    quantity_open = quantity_in - quantity_closed.
    """

    def __init__(self, base_asset: A, record_in: RI):

        validate_precision(record_in.quantity, base_asset.quantum)

        if record_in.operation.direction != DirectionEnum.IN:
            raise ValueError(f"Direction of the record-in must always be {DirectionEnum.IN!r}")

        self._base_asset: A = base_asset
        self._record_in: RI = record_in
        self._records_out: List[RO] = []

    @property
    def base_asset(self) -> A:
        return self._base_asset

    @property
    def record_in(self) -> RI:
        return self._record_in

    @property
    def records_out(self) -> Tuple[RO, ...]:
        return tuple(self._records_out)

    @property
    def last_record(self) -> RI | RO:
        return self._record_in if not self._records_out else self._records_out[-1]

    @property
    def quantity_closed(self) -> Decimal:
        return safe_sum(r_out.quantity for r_out in self._records_out)

    @property
    def quantity_open(self) -> Decimal:
        return self._record_in.quantity - self.quantity_closed

    @property
    def is_open(self) -> bool:
        return self.quantity_open > Decimal("0")

    @property
    def is_closed(self) -> bool:
        return not self.is_open

    def reduce(self, record_out: RO) -> Tuple[RO, RO] | None:
        if self.is_closed:
            raise ValueError("Lot already closed")

        validate_precision(record_out.quantity, self._base_asset.quantum)

        if record_out.operation.direction != DirectionEnum.OUT:
            raise ValueError(f"Record-out direction must always be {DirectionEnum.OUT!r}")

        if not self.has_valid_datetime(record_out):
            raise ValueError("Records must be in ascending order by date and time")

        quantity_open = self.quantity_open
        if self.quantity_open < record_out.quantity:
            record_closing, record_remaining = record_out.split(quantity_open)
            self._records_out.append(record_closing)
            return record_closing, record_remaining

        self._records_out.append(record_out)
        return None

    def has_valid_datetime(self, record_out: RO) -> bool:
        last_dt: datetime = self.last_record.datetime
        return last_dt <= record_out.datetime
