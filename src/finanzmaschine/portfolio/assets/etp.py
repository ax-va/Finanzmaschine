from dataclasses import dataclass
from typing import TypeVar, Generic

from finanzmaschine.portfolio.assets.base_asset import BaseAsset
from finanzmaschine.portfolio.assets.security import Security

A = TypeVar("A", bound=BaseAsset)


@dataclass(frozen=True)
class Etp(Security[A]):
    underlying_asset: A
