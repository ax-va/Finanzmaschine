from dataclasses import dataclass

from finanzmaschine.catalog.asset_enum import Asset
from finanzmaschine.core.market.instrument import Instrument


@dataclass(frozen=True)
class Share(Instrument):
    asset: Asset | None = None

    def require_asset(self) -> Asset:
        if self.asset is None:
            raise ValueError("Share has no underlying asset.")
        return self.asset
