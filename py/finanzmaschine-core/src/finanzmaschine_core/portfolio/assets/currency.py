from dataclasses import dataclass

from finanzmaschine_core.portfolio.assets.asset import Asset


@dataclass(frozen=True)
class Currency(Asset):
    pass
