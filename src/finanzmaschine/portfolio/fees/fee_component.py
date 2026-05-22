from dataclasses import dataclass
from decimal import Decimal

from finanzmaschine.portfolio.assets import Asset


@dataclass(frozen=True)
class FeeComponent:
    amount: Decimal
    asset: Asset

    def __post_init__(self) -> None:
        if not (self.amount >= Decimal("0")):
            raise ValueError("Fee amount must be not negative")
