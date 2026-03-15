from finanzmaschine.catalog.asset_enum import Asset
from finanzmaschine.catalog.instrument_registry import registry
from finanzmaschine.core.market.share import Share


TON_ETP_BY_21SHARES = registry.register(
    Share(
        isin="CH1297762812",
        name="21Shares Toncoin Staking ETP",
        asset=Asset.TON,
    )
)