from enum import Enum

class Mode(Enum):
    VACUUM = "VACUUM"
    ACCUMULATOR = "ACCUMULATOR"
    HUNTER = "HUNTER"


def detect_mode(
    price: float,
    vac_upper_bound: float,
    acc_upper_bound: float,
) -> Mode:
    if price <= vac_upper_bound:
        return Mode.VACUUM
    elif price <= acc_upper_bound:
        return Mode.ACCUMULATOR
    else:
        return Mode.HUNTER
