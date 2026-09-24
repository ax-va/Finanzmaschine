from dataclasses import dataclass

from finanzmaschine_accounting.portfolio.assets.asset import Asset
from finanzmaschine_accounting.portfolio.assets.security import Security


@dataclass(frozen=True)
class Etp[U: Asset](Security):
    underlying_asset: U
