import datetime

from lot import Lot


class Tranche:
    def __init__(
        self,
        lot: Lot,
        local_high: float,
        profit_pct: float = 0.2,  # +20%
        loss_pct: float = 0.4,  # -40%
        vac_upper: float = None,
        acc_upper: float = None,
    ):
        self.lot = lot
        self.local_high = local_high
        self.profit_pct = profit_pct
        self.loss_pct = loss_pct
        self.vac_upper = (
            vac_upper
            if vac_upper is not None
            else self.local_high * (1 - self.loss_pct)
        )
        # Can switch to HUNTER if:
        # entry_price * (1 - p) >= vac_upper
        # <=>
        # entry_price >= vac_upper / (1 - p)
        # Next bind `profit_pct` and `loss_pct` together:
        # entry_price >= vac_upper / 2 * (1 / (1 - profit_pct) + 1 / (1 - loss_pct))
        self.acc_upper = (
            acc_upper
            if acc_upper is not None
            else self.vac_upper / 2 * (1 / (1 - self.profit_pct) + 1 / (1 - self.loss_pct))
        )

    @property
    def start_date(self) -> datetime.date:
        return self.lot.price_bought_dt.date()

    @property
    def limit_order(self) -> float:
        return self.lot.price_bought * (1 + self.profit_pct)

    @property
    def stop_loss(self) -> float:
        stop_loss_raw = self.lot.price_bought * (1 - self.loss_pct)
        stop_loss = max(self.vac_upper, stop_loss_raw)
        return stop_loss