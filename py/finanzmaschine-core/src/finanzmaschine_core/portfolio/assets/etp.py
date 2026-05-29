from dataclasses import dataclass

from finanzmaschine_core.portfolio.assets.asset import Asset
from finanzmaschine_core.portfolio.assets.security import Security


@dataclass(frozen=True)
class Etp[U: Asset](Security):
    underlying_asset: U
