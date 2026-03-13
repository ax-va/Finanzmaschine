from finanzmaschine.core.market import Asset
from finanzmaschine.core.market.exchange import Exchange
from finanzmaschine.core.market.instruments import Etp

COINSHARES_PHYSICAL_STAKED_ETH = Etp(
    isin="GB00BLD4ZM24",
    name="CoinShares Physical Staked Ethereum",
    country_data={"DE": {"WKN": "A3GQ2N"}},
    tickers={Exchange.EIX: "CETH"},
    asset=Asset.ETH,
)
