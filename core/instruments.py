from dataclasses import dataclass, field
from typing import Dict

from core.asset import Asset
from core.exchange import Exchange


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


COINSHARES_PHYSICAL_STAKED_ETH = Etp(
    isin="GB00BLD4ZM24",
    name="CoinShares Physical Staked Ethereum",
    local_ids={"WKN": "A3GQ2N"},
    tickers={Exchange.EIX: "CETH"},
    asset=Asset.ETH,
)
