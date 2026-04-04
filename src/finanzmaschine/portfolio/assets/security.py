from dataclasses import dataclass

from finanzmaschine.portfolio.assets.asset import Asset


@dataclass(frozen=True)
class Security(Asset):
    pass
