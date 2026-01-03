import datetime
import math

from mode import Mode


class Tranche:
    def __init__(
        self,
        share_lot: ShareLot,
        asset_local_high: float,
        asset_profit_pct: float = 0.2,  # +20%
        asset_loss_pct: float = 0.4,  # -40%
        asset_vac_upper: float = None,
        asset_acc_upper: float = None,
    ):
        self.share_lot = share_lot
        self.asset_local_high = asset_local_high
        self.asset_profit_pct = asset_profit_pct
        self.asset_loss_pct = asset_loss_pct
        self.asset_vac_upper = (
            asset_vac_upper
            if asset_vac_upper is not None
            else self.asset_local_high * (1 - self.asset_loss_pct)
        )
        # Can switch to HUNTER if:
        # price * (1 - p) >= vac_upper
        # <=> price >= vac_upper / (1 - p)
        # Next bind `profit_pct` and `loss_pct` via the geometric mean:
        self.asset_acc_upper = (
            asset_acc_upper
            if asset_acc_upper is not None
            else self.asset_vac_upper / math.sqrt((1 - self.asset_profit_pct) * (1 - self.asset_loss_pct))
        )

    @property
    def start_date(self) -> datetime.date:
        return self.share_lot.price_bought_dt.date()

    @property
    def asset_limit_order(self) -> float:
        return self.share_lot.asset_lot.price_bought * (1 + self.asset_profit_pct)

    @property
    def asset_stop_loss(self) -> float:
        asset_stop_loss_raw = self.share_lot.asset_lot.price_bought * (1 - self.asset_loss_pct)
        asset_stop_loss = max(self.asset_vac_upper, asset_stop_loss_raw)
        return asset_stop_loss

    def detect_mode(self, asset_price: float) -> Mode:
        if asset_price <= self.asset_vac_upper:
            return Mode.VACUUM
        elif asset_price <= self.asset_acc_upper:
            return Mode.ACCUMULATOR
        else:
            return Mode.HUNTER