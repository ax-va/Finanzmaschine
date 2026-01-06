import datetime as dt
from typing import override

from finanzmaschine.core.lots.asset_lot import AssetLot
from finanzmaschine.core.lots.nominal_lot import NominalLot
from finanzmaschine.core.lots.share_lot_record import ShareLotRecord
from finanzmaschine.core.market.instruments import Share


class ShareLot(NominalLot[ShareLotRecord]):
    """
    A nominal lot corresponding to a share-based instrument.

    Units are invariant in share terms.
    Each share unit carries an entitlement to an underlying asset.
    """

    record_cls = ShareLotRecord

    def __init__(self, share: Share):
        super().__init__()
        self.share: Share = share
        self.asset_lot = AssetLot(self.share.require_asset())

    @override
    def record_in(
        self,
        *,
        units: float,  # share units to buy
        price: float,
        datetime: dt.datetime,
        entitlement: float,  # asset units per a share unit when buying
        **kwargs,
    ) -> float:
        assert entitlement > 0

        super().record_in(
            units=units,
            price=price,
            datetime=datetime,
            entitlement=entitlement,
            **kwargs,
        )
        cash_in: float = units * price
        return cash_in

    @override
    def record_out(
        self,
        *,
        units: float,  # share units to sell
        price: float,
        datetime: dt.datetime,
        entitlement: float,  # asset units per a share unit when selling
        **kwargs,
    ) -> float:
        assert entitlement > 0

        super().record_out(
            units=units,
            price=price,
            datetime=datetime,
            entitlement=entitlement
        )
        cash_out: float = units * price
        return cash_out


def record_share_lot_in(
    share_lot: ShareLot,
    share_units: float,  # share units to buy
    share_price: float,
    datetime: dt.datetime,
    entitlement: float,  # asset units per a share unit when buying
) -> float:
    share_lot.asset_lot.record_in(
        units=share_units * entitlement,  # implied units
        price=share_price / entitlement,  # implied price
        datetime=datetime,
    )
    cash_in: float = share_lot.record_in(
        units=share_units,
        price=share_price,
        datetime=datetime,
        entitlement=entitlement,
    )
    return cash_in


def record_share_lot_out(
    share_lot: ShareLot,
    share_units: float,  # share units to sell
    share_price: float,
    datetime: dt.datetime,
    entitlement: float,  # asset units per a share unit when selling
) -> float:
    share_lot.asset_lot.record_out(
        units=share_units * entitlement,  # implied units
        price=share_price / entitlement,  # implied price
        datetime=datetime,
    )
    cash_out: float = share_lot.record_out(
        units=share_units,
        price=share_price,
        datetime=datetime,
        entitlement=entitlement,
    )
    return cash_out
