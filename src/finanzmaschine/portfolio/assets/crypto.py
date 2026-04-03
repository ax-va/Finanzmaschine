from dataclasses import dataclass

from finanzmaschine.portfolio.assets import BaseAsset


@dataclass(frozen=True)
class Crypto(BaseAsset):
    pass