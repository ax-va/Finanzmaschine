from dataclasses import dataclass
from typing import TypeVar, Generic

from finanzmaschine.portfolio.assets import Etp
from finanzmaschine.portfolio.assets.base_asset import BaseAsset
from finanzmaschine.portfolio.assets.crypto import Crypto

A = TypeVar("A", bound=BaseAsset)


@dataclass(frozen=True)
class CryptoEtp(Etp["CryptoEtp", Crypto]):
    pass