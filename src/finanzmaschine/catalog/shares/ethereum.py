from finanzmaschine.catalog import registry
from finanzmaschine.catalog.asset_enum import Asset
from finanzmaschine.core.market.share import Share

COINSHARES_PHYSICAL_STAKED_ETH = Share(
    isin="GB00BLD4ZM24",
    name="CoinShares Physical Staked Ethereum",
    asset=Asset.ETH,
)

registry.register(COINSHARES_PHYSICAL_STAKED_ETH)

