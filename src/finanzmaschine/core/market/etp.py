from dataclasses import dataclass

from finanzmaschine.core.market.share import Share


@dataclass(frozen=True)
class Etp(Share):
    pass