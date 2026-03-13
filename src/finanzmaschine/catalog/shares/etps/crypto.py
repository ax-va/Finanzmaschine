from finanzmaschine.catalog import registry
from finanzmaschine.catalog.asset_enum import Asset
from finanzmaschine.catalog.exchange_enum import Exchange
from finanzmaschine.core.market.etp import Etp

COINSHARES_PHYSICAL_STAKED_ETH = Etp(
    isin="GB00BLD4ZM24",
    name="CoinShares Physical Staked Ethereum",
    country_data={"DE": {"WKN": "A3GQ2N"}},
    tickers={Exchange.EIX: "CETH"},
    asset=Asset.ETH,
)

registry.register(COINSHARES_PHYSICAL_STAKED_ETH)

