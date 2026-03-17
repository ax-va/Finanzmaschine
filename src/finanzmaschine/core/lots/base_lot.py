from datetime import datetime
from decimal import Decimal
from math import fsum
from typing import Tuple, Type, TypeVar, Any, Generic

from finanzmaschine.catalog.asset_enum import Asset
from finanzmaschine.core.lots.base_lot_record import BaseLotRecord
from finanzmaschine.utils.float_helper import round_to_zero

T = TypeVar("T", bound="BaseLot")
R = TypeVar("R", bound="BaseLotRecord")


class BaseLot(Generic[R]):
    """
    Base lot manages immutable lot records and its invariant is the base asset quantity.

    The open quantity is derived from the incoming quantity and all outgoing quantity:

    quantity_open = quantity_in - quantity_closed.
    """

    lot_record_cls: Type[R]

    def __init__(self, base_asset: Any):
        self.base_asset: Any = base_asset
        self.lot_record_in: R | None = None
        self.lot_records_out: Tuple[R, ...] = ()

    @property
    def records(self) -> Tuple[R, ...] | None:
        if self.lot_record_in is not None:
            return self.lot_record_in, *self.lot_records_out
        else:
            return None

    @property
    def quantity_closed(self) -> float:
        return fsum(r_out.quantity for r_out in self.lot_records_out)

    @property
    def quantity_open(self) -> float:
        return round_to_zero(self.lot_record_in.quantity - self.quantity_closed)

    @property
    def is_open(self) -> bool:
        return self.quantity_open > 0

    @property
    def is_closed(self) -> bool:
        return not self.is_open

    @classmethod
    def open(
        cls: Type[T],
        *,
        base_asset: Any,
        quantity: float,
        price: Decimal,
        quote_asset: Asset,
        fee: Decimal,
        fee_asset: Asset,
        dt: datetime,
        **kwargs: Any,
    ) -> T:

        lot = cls(base_asset)
        # noinspection PyProtectedMember
        lot._record_in(quantity, price, quote_asset, fee, fee_asset, dt, **kwargs)

        return lot

    def close_quantity(
        self,
        *,
        quantity: float,
        price: Decimal,
        quote_asset: Asset,
        fee: Decimal,
        fee_asset: Asset,
        dt: datetime,
        **kwargs: Any,
    ) -> None:
        self._record_out(quantity, price, quote_asset, fee, fee_asset, dt, **kwargs)

    def _record_in(
        self,
        quantity: float,
        price: Decimal,
        quote_asset: Asset,
        fee: Decimal,
        fee_asset: Asset,
        dt: datetime,
        **kwargs: Any,
    ) -> None:
        self._validate_record(quantity, price, fee, **kwargs)

        self.lot_record_in = self.lot_record_cls(
            quantity, price, quote_asset, fee, fee_asset, dt, **kwargs
        )

    def _record_out(
        self,
        quantity: float,
        price: Decimal,
        quote_asset: Asset,
        fee: Decimal,
        fee_asset: Asset,
        dt: datetime,
        **kwargs: Any,
    ) -> None:
        self._validate_record_out(quantity, price, fee, dt, **kwargs)

        lot_record_out = self.lot_record_cls(quantity, price, quote_asset, fee, fee_asset, dt, **kwargs)
        self.lot_records_out = *self.lot_records_out, lot_record_out

    @staticmethod
    def _validate_record(
        quantity: float,
        price: Decimal,
        fee: Decimal,
        **kwargs: Any,
    ) -> None:
        assert quantity > 0
        assert price > 0
        assert fee >= 0

    def _validate_record_out(
        self,
        quantity: float,
        price: Decimal,
        fee: Decimal,
        dt: datetime,
        **kwargs: Any,
    ) -> None:
        self._validate_record(quantity, price, fee, **kwargs)

        assert self.lot_record_in is not None
        assert self.lot_record_in.quantity > 0
        assert round_to_zero(self.quantity_open - quantity) >= 0
        assert self.lot_record_in.dt <= dt
        for record_out in self.lot_records_out:
            assert record_out.dt <= dt
