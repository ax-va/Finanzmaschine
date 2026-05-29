from dataclasses import dataclass
from decimal import Decimal
from typing import Tuple

from finanzmaschine_core.portfolio.assets import Asset
from finanzmaschine_core.portfolio.fees.fee_component import FeeComponent
from finanzmaschine_core.helpers.decimal_helper import safe_sum


@dataclass(frozen=True)
class Fee:
    components: Tuple[FeeComponent, ...]

    def get_total(self, quote_asset: Asset) -> Decimal:
        if all(c.asset == quote_asset for c in self.components):
            return safe_sum(c.amount for c in self.components)
        raise NotImplementedError("Multi-currency fees are not supported yet")