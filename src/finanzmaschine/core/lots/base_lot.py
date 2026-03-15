from datetime import datetime
from math import fsum
from typing import Tuple, Type, TypeVar, Any

from finanzmaschine.core.lots.currency_enum import Currency
from finanzmaschine.core.lots.lot_record import LotRecord


T = TypeVar("T", bound="BaseLot")

class BaseLot:
    """
    Base lot managing immutable lot records.
    """

    def __init__(self, **kwargs):
        self.lot_record_in: LotRecord | None = None
        self.lot_records_out: Tuple[LotRecord, ...] = ()
        self._units_closed: float = 0.0

    @property
    def units_closed(self) -> float:
        return fsum(r.units for r in self.lot_records_out)

    @property
    def records(self) -> Tuple[LotRecord, ...] | None:
        if self.lot_record_in is not None:
            return self.lot_record_in, *self.lot_records_out
        else:
            return None

    @classmethod
    def open(
        cls: Type[T],
        *,
        units: float,
        price: float,
        price_currency: Currency,
        fee: float,
        fee_currency: Currency,
        dt: datetime,
        **kwargs: Any,
    ) -> T:

        constructor_kwargs = cls._constructor_kwargs(kwargs)
        lot = cls(**constructor_kwargs)

        # noinspection PyProtectedMember
        lot._record_in(units, price, price_currency, fee, fee_currency, dt)

        # remaining kwargs
        post_kwargs = {k: v for k, v in kwargs.items() if k not in constructor_kwargs}
        # noinspection PyProtectedMember
        lot._post_open(**post_kwargs)

        return lot

    def close_units(
        self,
        *,
        units: float,
        price: float,
        price_currency: Currency,
        fee: float,
        fee_currency: Currency,
        dt: datetime,
        **kwargs: Any,
    ) -> None:
        self._record_out(units, price, price_currency, fee, fee_currency, dt)

    @classmethod
    def _constructor_kwargs(cls, kwargs: dict) -> dict:
        return {}

    def _post_open(self, **kwargs) -> None:
        pass

    def _record_in(
        self,
        units: float,
        price: float,
        price_currency: Currency,
        fee: float,
        fee_currency: Currency,
        dt: datetime,
    ) -> None:
        self._validate_record(units, price, fee)

        self.lot_record_in = LotRecord(units, price, price_currency, fee, fee_currency, dt)

    def _record_out(
        self,
        units: float,
        price: float,
        price_currency: Currency,
        fee: float,
        fee_currency: Currency,
        dt: datetime,
    ) -> None:
        self._validate_record_out(units, price, fee, dt)

        lot_record_out = LotRecord(units, price, price_currency, fee, fee_currency, dt)
        self.lot_records_out = *self.lot_records_out, lot_record_out

    @staticmethod
    def _validate_record(
        units: float,
        price: float,
        fee: float,
    ) -> None:
        assert units > 0
        assert price > 0
        assert fee >= 0

    def _validate_record_out(
        self,
        units: float,
        price: float,
        fee: float,
        dt: datetime,
    ) -> None:
        self._validate_record(units, price, fee)
        assert self.lot_record_in is not None
        assert self.lot_record_in.units > 0
        assert self.lot_record_in.dt <= dt
        for record_out in self.lot_records_out:
            assert record_out.dt <= dt
