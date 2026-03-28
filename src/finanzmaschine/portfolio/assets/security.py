from dataclasses import dataclass

from finanzmaschine.portfolio.assets.base_asset import BaseAsset


@dataclass(frozen=True)
class Security(BaseAsset):
    pass
