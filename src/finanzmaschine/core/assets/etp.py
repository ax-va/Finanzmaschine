from dataclasses import dataclass

from finanzmaschine.core.assets.asset import Asset
from finanzmaschine.core.assets.security import Security


@dataclass(frozen=True)
class Etp(Security):
    underlying_asset: Asset
