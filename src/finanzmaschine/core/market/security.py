from dataclasses import dataclass

from finanzmaschine.core.market.asset import Asset


@dataclass(frozen=True)
class Security(Asset):
    isin: str
