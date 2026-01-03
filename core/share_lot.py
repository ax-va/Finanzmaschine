import datetime

from asset_lot import AssetLot
from lot import Lot


class ShareLot(Lot):
    def __init__(
        self,
        isin: str,
        share_name: str = None,
        asset_name: str = None,
    ):
        self.isin = isin
        self.name = share_name
        self.asset_lot = AssetLot(asset_name)
        super().__init__()


def buy_share_lot(
    share_lot: ShareLot,
    cash: float,
    share_price: float,
    asset_price: float,
    price_dt: datetime.datetime,
) -> None:
    share_lot.buy(cash, share_price, price_dt)
    share_lot.asset_lot.buy(cash, asset_price, price_dt)


def sell_share_lot(
    share_lot: ShareLot,
    share_price: float,
    asset_price: float,
    price_dt: datetime.datetime,
) -> float:
    cash = share_lot.sell(share_price, price_dt)
    share_lot.asset_lot.sell(asset_price, price_dt)
    return cash