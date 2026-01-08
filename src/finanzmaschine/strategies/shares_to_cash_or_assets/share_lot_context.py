import math
from datetime import date

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
        asset_profit_pct: float | None = 0.2,  # +20%
        asset_loss_pct: float | None = 0.4,  # -40%
        asset_local_high: float | None = None,
        asset_vac_upper_bound: float | None = None,
        asset_acc_upper_bound: float | None = None,
    ):
        if asset_profit_pct is not None:
            assert asset_profit_pct > 0
        if asset_loss_pct is not None:
            assert 0 < asset_loss_pct < 1
        if asset_local_high is not None:
            assert asset_local_high > 0
        if asset_vac_upper_bound is not None:
            assert asset_vac_upper_bound >= 0
            if asset_local_high is not None:
                assert asset_vac_upper_bound <= asset_local_high
        if asset_acc_upper_bound is not None:
            assert asset_acc_upper_bound >= 0
            if asset_local_high is not None:
                assert asset_acc_upper_bound <= asset_local_high
        if asset_vac_upper_bound is not None and asset_acc_upper_bound is not None:
            assert asset_vac_upper_bound <= asset_acc_upper_bound

        self.share_lot: ShareLot = share_lot
        self.asset_local_high: float | None = asset_local_high
        self.asset_profit_pct: float | None = asset_profit_pct
        self.asset_loss_pct: float | None = asset_loss_pct

        # VACUUM mode upper bound for asset price
        if asset_vac_upper_bound is None:
            if (
                self.asset_local_high is not None
                and self.asset_loss_pct is not None
            ):
                asset_vac_upper_bound = self.asset_local_high * (1 - self.asset_loss_pct)
        self.asset_vac_upper_bound: float | None = asset_vac_upper_bound

        if asset_acc_upper_bound is None:
            if (
                self.asset_vac_upper_bound is not None
                and self.asset_profit_pct is not None
                and self.asset_loss_pct is not None
                and self.asset_profit_pct < 1
            ):
                # ACCUMULATOR mode upper bound for asset price:
                # Switch to the HUNTER mode if
                # price * (1 - p) >= vac_upper_bound <=> price >= vac_upper_bound / (1 - p) =: acc_upper_bound.
                # Next bind `profit_pct` and `loss_pct` via the geometric mean:
                asset_acc_upper_bound =self.asset_vac_upper_bound / math.sqrt(
                    (1 - self.asset_profit_pct) * (1 - self.asset_loss_pct)
                )
            else:
                # no ACCUMULATOR mode for asset price
                asset_acc_upper_bound = self.asset_vac_upper_bound
        self.asset_acc_upper_bound: float | None = asset_acc_upper_bound

    @property
    def asset_limit_order_price(self) -> float | None:
        if self.asset_profit_pct is not None:
            return self.share_lot.asset_lot.lot_record_in.price * (1 + self.asset_profit_pct)
        else:
            return None

    @property
    def asset_stop_loss_price(self) -> float | None:
        if self.asset_loss_pct is not None:
            asset_stop_loss: float = self.share_lot.asset_lot.lot_record_in.price * (1 - self.asset_loss_pct)
            if self.asset_vac_upper_bound is not None:
                asset_stop_loss: float = max(self.asset_vac_upper_bound, asset_stop_loss)
            return asset_stop_loss
        else:
            return None

    @property
    def date_in(self) -> date:
        return self.share_lot.lot_record_in.datetime.date()

    # @property
    # def is_tax_exempt(self):
    #     return date.today() >= self.date_in + relativedelta(years=1)
