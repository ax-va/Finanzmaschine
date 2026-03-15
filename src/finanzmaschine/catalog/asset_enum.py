from enum import Enum


class Asset(Enum):
    ETH = "ETH"
    TON = "TON"


def parse_asset(s: str) -> Asset:
    try:
        return Asset[s.upper()]
    except KeyError:
        raise ValueError(f"Unknown asset: {s}")
