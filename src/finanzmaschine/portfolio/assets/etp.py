from dataclasses import dataclass
from typing import TypeVar, Generic

from finanzmaschine.portfolio.assets.asset import Asset
from finanzmaschine.portfolio.assets.security import Security

U = TypeVar("U", bound=Asset)


@dataclass(frozen=True)
class Etp(Security, Generic[U]):
    underlying_asset: U
