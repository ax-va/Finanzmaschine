from finanzmaschine.catalog import registry
from finanzmaschine.catalog.asset_enum import Asset
from finanzmaschine.catalog.exchange_enum import Exchange

instrument = registry.get_by_isin("GB00BLD4ZM24")
print(instrument)
instrument = registry.get_by_exchange_ticker(Exchange.EIX, "CETH")
print(instrument)
instrument = registry.get_by_asset(Asset.ETH)
print(instrument)
instrument = registry.get_by_wkn("A3GQ2N")
print(instrument)