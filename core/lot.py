import datetime


class Lot:
    def __init__(self):
        self.amount: float = 0
        self.price_bought: float = None
        self.price_bought_dt: datetime.datetime = None
        self.price_sold: float = None
        self.price_sold_dt: float = None

    def buy(
        self,
        cash: float,
        price: float,
        price_dt: datetime.datetime,
    ) -> None:
        assert cash > 0
        assert self.amount == 0

        self.amount = cash / price
        self.price_bought = price
        self.price_bought_dt = price_dt

    def sell(
        self,
        price: float,
        price_dt: datetime.datetime,
    ) -> float:
        assert self.amount > 0

        cash = self.amount * price
        self.price_sold = price
        self.price_sold_dt = price_dt
        return cash
