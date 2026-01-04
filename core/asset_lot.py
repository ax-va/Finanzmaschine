import datetime

from core.asset import Asset
from core.lot import Lot


class AssetLot(Lot):
    def __init__(self, asset: Asset):
        super().__init__()
        self.asset: str = asset
        self.amount_bought: float = 0.0
        self.amount_sold: float | None = None


    def buy(
        self,
        share_units: float,
        entitlement: float,  # asset per share
        price_implied: float,
        price_dt: datetime.datetime,
    ) -> None:
        assert share_units > 0
        assert entitlement > 0
        assert self.amount_bought == 0

        self.amount_bought: float = share_units * entitlement
        self.price_bought: float = price_implied
        self.price_bought_dt: datetime.datetime = price_dt

    def sell(
        self,
        share_units: float,
        entitlement: float,  # asset per share
        price_implied: float,
        price_dt: datetime.datetime,
    ) -> None:
        assert share_units > 0
        assert entitlement > 0
        assert self.amount_bought > 0

        self.amount_sold: float = share_units * entitlement
        self.price_sold: float = price_implied
        self.price_sold_dt: datetime.datetime = price_dt
