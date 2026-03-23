from dataclasses import dataclass

from finanzmaschine.core.assets.base_asset import BaseAsset


@dataclass(frozen=True)
class Security(BaseAsset):
    pass
