import datetime
import math

from finanzmaschine.core.lots import ShareLot


class ShareLotContext:
    """
    Based on the share lot context, the machine determines the next steps.

    The share lot context defines the initial conditions, constraints,
    and derives thresholds used by the machine to decide how to proceed.
    """

    def __init__(
        self,
        share_lot: ShareLot,
        asset_local_high: float,
        asset_profit_pct: float = 0.2,  # +20%
        asset_loss_pct: float = 0.4,  # -40%
        asset_vac_upper_bound: float = None,
        asset_acc_upper_bound: float = None,
    ):
        self.share_lot: ShareLot = share_lot
        self.asset_local_high: float = asset_local_high
        self.asset_profit_pct: float = asset_profit_pct
        self.asset_loss_pct: float = asset_loss_pct
        # VACUUM upper bound
        self.asset_vac_upper_bound: float = (
            asset_vac_upper_bound
            if asset_vac_upper_bound is not None
            else self.asset_local_high * (1 - self.asset_loss_pct)
        )
        # ACCUMULATOR upper bound: Can switch to HUNTER if
        # price * (1 - p) >= vac_upper_bound <=> price >= vac_upper_bound / (1 - p) =: acc_upper_bound.
        # Next bind `profit_pct` and `loss_pct` via the geometric mean:
        self.asset_acc_upper_bound: float = (
            asset_acc_upper_bound
            if asset_acc_upper_bound is not None
            else self.asset_vac_upper_bound / math.sqrt(
                (1 - self.asset_profit_pct) * (1 - self.asset_loss_pct)
            )
        )

    @property
    def asset_limit_order_price(self) -> float:
        return self.share_lot.asset_lot.price_in * (1 + self.asset_profit_pct)

    @property
    def asset_stop_loss_price(self) -> float:
        asset_stop_loss_raw: float = self.share_lot.asset_lot.price_in * (1 - self.asset_loss_pct)
        asset_stop_loss: float = max(self.asset_vac_upper_bound, asset_stop_loss_raw)
        return asset_stop_loss

    @property
    def date_in(self) -> datetime.date:
        return self.share_lot.datetime_in.date()
