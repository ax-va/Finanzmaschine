from dataclasses import dataclass
from typing import TypeVar, Generic

from finanzmaschine.portfolio.assets.base_asset import BaseAsset
from finanzmaschine.portfolio.assets.security import Security

U = TypeVar("U", bound=BaseAsset)


@dataclass(frozen=True)
class Etp(Security, Generic[U]):
    underlying_asset: U
