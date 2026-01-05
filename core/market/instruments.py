from dataclasses import dataclass, field
from typing import Dict

from core.market.asset import Asset
from core.market.exchange import Exchange


@dataclass(frozen=True)
class Instrument:
    isin: str
    name: str
    local_ids: Dict[str, str] = field(default_factory=dict)
    tickers: Dict[Exchange, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Share(Instrument):
    asset: Asset | None = None

    def require_asset(self) -> Asset:
        if self.asset is None:
            raise ValueError("Share has no underlying asset.")
        return self.asset


@dataclass(frozen=True)
class Etp(Share):
    pass
