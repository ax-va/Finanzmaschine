from datetime import datetime
from typing import override

from finanzmaschine.core.lots.asset_lot import AssetLot
from finanzmaschine.core.lots.currency_enum import Currency
from finanzmaschine.core.lots.nominal_lot import NominalLot
from finanzmaschine.core.market.share import Share


class ShareLot(NominalLot):
    """
    A lot corresponding to a share-based instrument.

    Units are invariant in share terms: units_open = units_in - units_out_total.
    Each share unit carries an entitlement to an underlying asset.
    """

    def __init__(self, share: Share):
        super().__init__()
        share.require_asset()
        self.share: Share = share
        self.asset_lot: AssetLot | None = None

    @override
    def close_units(
        self,
        *,
        units: float,
        price: float,
        price_currency: Currency,
        fee: float,
        fee_currency: Currency,
        dt: datetime,
        entitlement: float | None = None,
    ) -> None:
        super().close_units(
            units=units,
            price=price,
            price_currency=price_currency,
            fee=fee,
            fee_currency=fee_currency,
            dt=dt,
        )

        if entitlement is None:
            return

        # implied units
        asset_units = units * entitlement
        # implied price
        asset_price = price / entitlement

        assert self.asset_lot is not None

        self.asset_lot.close_units(
            units=asset_units,
            price=asset_price,
            price_currency=price_currency,
            fee=fee,
            fee_currency=fee_currency,
            dt=dt,
        )

    @override
    @classmethod
    def _constructor_kwargs(
        cls,
        kwargs: dict,
    ) -> dict:
        return {"share": kwargs["share"]}

    @override
    def _post_open(
        self,
        entitlement: float | None = None,
    ) -> None:
        if entitlement is None:
            return

        assert self.lot_record_in is not None

        # implied units
        asset_units = self.lot_record_in.units * entitlement
        # implied price
        asset_price = self.lot_record_in.price / entitlement

        self.asset_lot = AssetLot.open(
            units=asset_units,
            price=asset_price,
            price_currency=self.lot_record_in.price_currency,
            fee=self.lot_record_in.fee,
            fee_currency=self.lot_record_in.fee_currency,
            dt=self.lot_record_in.dt,
        )
