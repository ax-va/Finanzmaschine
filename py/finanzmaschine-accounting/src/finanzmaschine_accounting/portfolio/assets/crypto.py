from dataclasses import dataclass

from finanzmaschine_accounting.portfolio.assets.asset import Asset


@dataclass(frozen=True)
class Crypto(Asset):
    pass