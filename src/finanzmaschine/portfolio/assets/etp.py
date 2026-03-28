from dataclasses import dataclass

from finanzmaschine.portfolio.assets.base_asset import BaseAsset
from finanzmaschine.portfolio.assets.security import Security


@dataclass(frozen=True)
class Etp(Security):
    underlying_asset: BaseAsset
