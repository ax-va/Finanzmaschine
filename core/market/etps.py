from core.market import Asset
from core.market.exchange import Exchange
from core.market.instruments import Etp

COINSHARES_PHYSICAL_STAKED_ETH = Etp(
    isin="GB00BLD4ZM24",
    name="CoinShares Physical Staked Ethereum",
    local_ids={"WKN": "A3GQ2N"},
    tickers={Exchange.EIX: "CETH"},
    asset=Asset.ETH,
)
