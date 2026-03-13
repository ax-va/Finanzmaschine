from datetime import datetime

from finanzmaschine.core.lots.asset_lot import AssetLot
from finanzmaschine.core.lots.lot_state import LotState
from finanzmaschine.core.lots.nominal_lot import NominalLot
from finanzmaschine.core.market.instruments import Share


class ShareLot(NominalLot):
    """
    A nominal lot corresponding to a share-based instrument.

    Units are invariant in share terms: units_open = units_in - units_out_total.
    Each share unit carries an entitlement to an underlying asset.

    Examples of such instruments include ETPs such as ETFs, ETNs, and ETCs.
    """

    def __init__(self, share: Share):
        super().__init__()
        self.share: Share = share
        self.asset_lot = AssetLot(self.share.require_asset())


def open_share_lot(
    lot: ShareLot,
    units: float,  # share units to open
    price: float,
    fee: float,
    dt: datetime,
    entitlement: float | None = None,  # asset units per a share unit when buying
) -> float:
    if entitlement is not None:
        asset_units = units * entitlement  # implied units
        asset_price = price / entitlement  # implied price
        lot.asset_lot.record_in(
            units=asset_units,
            price=asset_price,
            fee=fee,
            dt=dt,
        )

    lot.record_in(
        units=units,
        price=price,
        fee=fee,
        dt=dt,
    )

    cash_out: float = -(units * price + fee)
    return cash_out


def close_share_lot_part(
    lot: ShareLot,
    units: float,  # share units to close
    price: float,
    fee: float,
    dt: datetime,
    entitlement: float | None = None,  # asset units per a share unit when selling
) -> float:
    if (
        entitlement is not None and
        lot.asset_lot.state == LotState.OPEN
    ):
        asset_units = units * entitlement  # implied units
        asset_price = price / entitlement  # implied price
        lot.asset_lot.record_out(
            units=asset_units,
            price=asset_price,
            fee=fee,
            dt=dt,
        )

    lot.record_out(
        units=units,
        price=price,
        fee=fee,
        dt=dt,
    )

    if lot.state == LotState.CLOSED:
        lot.asset_lot.state = LotState.CLOSED

    cash_in: float = units * price - fee
    return cash_in
