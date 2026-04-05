from dataclasses import dataclass

from finanzmaschine.portfolio.assets.asset import Asset
from finanzmaschine.portfolio.assets.security import Security


@dataclass(frozen=True)
class Etp[U: Asset](Security):
    underlying_asset: U
