from dataclasses import dataclass

from finanzmaschine.core.assets.asset import Asset


@dataclass(frozen=True)
class Security(Asset):
    pass
