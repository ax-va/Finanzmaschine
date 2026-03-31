from dataclasses import dataclass
from typing import TypeVar

from finanzmaschine.portfolio.assets import BaseAsset

A = TypeVar("A", bound=BaseAsset)


@dataclass(frozen=True)
class Currency(BaseAsset[A]):
    pass
