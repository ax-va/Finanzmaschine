import datetime

from asset_lot import AssetLot
from lot import Lot


class ShareLot(Lot):
    def __init__(
        self,
        share_isin: str,
        share_name: str,
        asset_name: str,
    ):
        self.isin: str = share_isin
        self.name: str = share_name
        self.units: float = 0
        self.asset_lot = AssetLot(asset_name)
        self.entitlement_bought: float | None = None
        self.entitlement_sold: float | None = None
        super().__init__()

    def buy(
        self,
        cash_in: float,
        price: float,
        price_dt: datetime.datetime,
    ) -> None:
        assert cash_in > 0
        assert price > 0
        assert self.units == 0

        self.units: float = cash_in / price
        self.price_bought: float = price
        self.price_bought_dt: datetime.datetime = price_dt

    def sell(
        self,
        price: float,
        price_dt: datetime.datetime,
    ) -> float:
        assert self.units > 0

        cash_out: float = self.units * price
        self.price_sold: float = price
        self.price_sold_dt: datetime.datetime = price_dt
        return cash_out


def buy_share_lot(
    share_lot: ShareLot,
    cash_in: float,
    share_price: float,
    entitlement: float,  # asset per share
    price_dt: datetime.datetime,
) -> None:
    share_lot.buy(cash_in, share_price, price_dt)
    share_lot.entitlement_bought = entitlement
    asset_price_implied: float = share_price / entitlement
    share_lot.asset_lot.buy(share_lot.units, entitlement, asset_price_implied, price_dt)


def sell_share_lot(
    share_lot: ShareLot,
    share_price: float,
    entitlement: float,  # asset per share
    price_dt: datetime.datetime,
) -> float:
    cash_out: float = share_lot.sell(share_price, price_dt)
    share_lot.entitlement_sold = entitlement
    asset_price_implied: float = share_price / entitlement
    share_lot.asset_lot.sell(share_lot.units, entitlement, asset_price_implied, price_dt)
    return cash_out
