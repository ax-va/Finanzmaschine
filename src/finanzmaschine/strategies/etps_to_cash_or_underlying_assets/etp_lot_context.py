import math
from datetime import date

from finanzmaschine.portfolio.lots import EtpLot


class ShareLotContext:
    """
    Based on the share lot context, the machine determines the next steps.

    The share lot context defines the initial conditions, constraints,
    and derives thresholds used by the machine to decide how to proceed.
    """

    def __init__(
        self,
        etp_lot: EtpLot,
        underlying_profit_pct: float | None = 0.2,  # +20%
        underlying_loss_pct: float | None = 0.4,  # -40%
        underlying_local_high: float | None = None,
        underlying_vac_upper_bound: float | None = None,
        underlying_acc_upper_bound: float | None = None,
    ):
        if underlying_profit_pct is not None:
            assert underlying_profit_pct > 0

        if underlying_loss_pct is not None:
            assert 0 < underlying_loss_pct < 1

        if underlying_local_high is not None:
            assert underlying_local_high > 0

        if underlying_vac_upper_bound is not None:
            assert underlying_vac_upper_bound >= 0

            if underlying_local_high is not None:
                assert underlying_vac_upper_bound <= underlying_local_high

        if underlying_acc_upper_bound is not None:
            assert underlying_acc_upper_bound >= 0

            if underlying_local_high is not None:
                assert underlying_acc_upper_bound <= underlying_local_high

        if underlying_vac_upper_bound is not None and underlying_acc_upper_bound is not None:
            assert underlying_vac_upper_bound <= underlying_acc_upper_bound

        self.etp_lot: EtpLot = etp_lot
        self.underlying_local_high = underlying_local_high
        self.underlying_profit_pct = underlying_profit_pct
        self.underlying_loss_pct = underlying_loss_pct

        # VACUUM mode upper bound for underlying price
        if underlying_vac_upper_bound is None:
            if self.underlying_local_high is not None and self.underlying_loss_pct is not None:
                underlying_vac_upper_bound = self.underlying_local_high * (
                    1 - self.underlying_loss_pct
                )
        self.underlying_vac_upper_bound = underlying_vac_upper_bound

        if underlying_acc_upper_bound is None:
            if (
                self.underlying_vac_upper_bound is not None
                and self.underlying_profit_pct is not None
                and self.underlying_loss_pct is not None
                and self.underlying_profit_pct < 1
            ):
                # ACCUMULATOR mode upper bound for underlying price:
                # Switch to the HUNTER mode if
                # price * (1 - p) >= vac_upper_bound <=> price >= vac_upper_bound / (1 - p) =: acc_upper_bound.
                # Next bind `profit_pct` and `loss_pct` via the geometric mean:
                underlying_acc_upper_bound = self.underlying_vac_upper_bound / math.sqrt(
                    (1 - self.underlying_profit_pct) * (1 - self.underlying_loss_pct)
                )
            else:
                # no ACCUMULATOR mode for underlying price
                underlying_acc_upper_bound = self.underlying_vac_upper_bound
        self.underlying_acc_upper_bound = underlying_acc_upper_bound

    @property
    def underlying_profit_price(self) -> float | None:
        if self.underlying_profit_pct is not None:
            underlying_price_in = self.etp_lot.record_in.price / self.etp_lot.record_in.entitlement
            return underlying_price_in * (1 + self.underlying_profit_pct)
        else:
            return None

    @property
    def underlying_loss_price(self) -> float | None:
        if self.underlying_loss_pct is not None:
            underlying_price_in = self.etp_lot.record_in.price / self.etp_lot.record_in.entitlement
            underlying_stop_loss = underlying_price_in * (1 - self.underlying_loss_pct)

            if self.underlying_vac_upper_bound is not None:
                underlying_stop_loss = max(
                    self.underlying_vac_upper_bound, underlying_stop_loss
                )
            return underlying_stop_loss
        else:
            return None

    @property
    def date_in(self) -> date:
        return self.etp_lot.record_in.dt.date()

    # @property
    # def is_tax_exempt(self):
    #     return date.today() >= self.date_in + relativedelta(years=1)
