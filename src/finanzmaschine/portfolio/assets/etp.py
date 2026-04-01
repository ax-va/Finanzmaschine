from dataclasses import dataclass
from typing import TypeVar, Generic

from finanzmaschine.portfolio.assets.base_asset import BaseAsset
from finanzmaschine.portfolio.assets.security import Security

E = TypeVar("E", bound="Etp")
U = TypeVar("U", bound=BaseAsset)


@dataclass(frozen=True)
class Etp(Security[E], Generic[E, U]):
    underlying_asset: U
