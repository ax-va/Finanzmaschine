import datetime
from typing import List

from core.positions.asset_lot import AssetLot
from core.market.instruments import Share
from core.positions.base_lot import BaseLot


class ShareLot(BaseLot):
    def __init__(self, share: Share):
        super().__init__()
        self.share: Share = share
        self.asset_lot = AssetLot(self.share.require_asset())
        self.entitlement_in: float | None = None  # asset per share
        self.entitlement_out_list: List[float] = []  # asset per share

    def buy(
        self,
        units_in: float,  # units to buy
        entitlement_in: float,  # asset units per a share unit when buying
        price_in: float,
        datetime_in: datetime.datetime,
    ) -> float:
        assert self.units_in == 0
        assert units_in > 0
        assert entitlement_in > 0
        assert price_in > 0

        cash_in: float = units_in * price_in
        self.units_in: float = units_in
        self.entitlement_in: float = entitlement_in
        self.price_in: float = price_in
        self.datetime_in: datetime.datetime = datetime_in
        return cash_in

    def sell(
        self,
        units_out: float,  # units to sell
        entitlement_out: float,  # asset units per a share unit when selling
        price_out: float,
        datetime_out: datetime.datetime,
    ) -> float:
        assert self.units_in > 0
        assert units_out > 0
        assert units_out <= self.units_open
        assert entitlement_out > 0
        assert price_out > 0

        cash_out: float = units_out * price_out
        self.units_out_list.append(units_out)
        self.entitlement_out_list.append(entitlement_out)
        self.price_out_list.append(price_out)
        self.datetime_out_list.append(datetime_out)
        return cash_out


def buy_share_lot(
    share_lot: ShareLot,
    share_units_in: float,  # share units to buy
    entitlement_in: float,  # asset units per a share unit when buying
    share_price_in: float,
    datetime_in: datetime.datetime,
) -> float:
    cash_in: float = share_lot.buy(
        units_in=share_units_in,
        entitlement_in=entitlement_in,
        price_in=share_price_in,
        datetime_in=datetime_in,
    )
    share_lot.asset_lot.buy(
        share_units_in=share_units_in,
        entitlement_in=entitlement_in,
        price_in_implied=share_price_in / entitlement_in,
        datetime_in=datetime_in,
    )
    return cash_in


def sell_share_lot(
    share_lot: ShareLot,
    share_units_out: float,  # share units to sell
    entitlement_out: float,  # asset units per a share unit when selling
    share_price_out: float,
    datetime_out: datetime.datetime,
) -> float:
    cash_out: float = share_lot.sell(
        units_out=share_units_out,
        entitlement_out=entitlement_out,
        price_out=share_price_out,
        datetime_out=datetime_out,
    )
    share_lot.asset_lot.sell(
        share_units_out=share_units_out,
        entitlement_out=entitlement_out,
        price_out_implied=share_price_out / entitlement_out,
        datetime_out=datetime_out,
    )
    return cash_out
