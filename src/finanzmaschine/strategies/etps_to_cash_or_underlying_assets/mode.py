from decimal import Decimal
from enum import Enum


class Mode(Enum):
    VACUUM = "VACUUM"
    ACCUMULATOR = "ACCUMULATOR"
    HUNTER = "HUNTER"


def detect_mode(
    price: Decimal,
    vac_upper_bound: Decimal,
    acc_upper_bound: Decimal,
) -> Mode:

    if price <= vac_upper_bound:
        return Mode.VACUUM

    elif vac_upper_bound < price <= acc_upper_bound:
        return Mode.ACCUMULATOR

    else:
        return Mode.HUNTER
