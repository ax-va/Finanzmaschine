from dataclasses import dataclass
from typing import TypeVar

from finanzmaschine.portfolio.assets.base_asset import BaseAsset

S = TypeVar("S", bound="Security")


@dataclass(frozen=True)
class Security(BaseAsset[S]):
    pass
