from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, eq=False, kw_only=True)
class FeeMixin:
    fee: Decimal

    def __post_init__(self) -> None:
        if not (self.fee >= Decimal("0")):
            raise ValueError("Fee amount must be not negative")
