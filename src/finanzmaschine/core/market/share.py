from dataclasses import dataclass

from finanzmaschine.catalog.asset_enum import Asset
from finanzmaschine.core.market.instrument import Instrument


@dataclass(frozen=True)
class Share(Instrument):
    shared_asset: Asset
