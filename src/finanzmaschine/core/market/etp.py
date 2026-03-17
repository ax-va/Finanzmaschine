from dataclasses import dataclass

from finanzmaschine.catalog.asset_enum import Asset
from finanzmaschine.core.market.security import Security


@dataclass(frozen=True)
class Etp(Security):
    underlying: Asset
