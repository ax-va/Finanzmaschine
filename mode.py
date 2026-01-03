from enum import Enum

class Mode(Enum):
    VACUUM = "VACUUM"
    ACCUMULATOR = "ACCUMULATOR"
    HUNTER = "HUNTER"


def detect_mode(entry_price, vac_upper, acc_upper) -> Mode:
    if entry_price <= vac_upper:
        return Mode.VACUUM
    elif entry_price <= acc_upper:
        return Mode.ACCUMULATOR
    else:
        return Mode.HUNTER
