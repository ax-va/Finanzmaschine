from pprint import pprint

from finanzmaschine.catalog import asset_registry

etp = asset_registry.get("GB00BLD4ZM24")
print(etp)
# Etp(id='GB00BLD4ZM24', name='CoinShares Physical Staked Ethereum', underlying_asset=Crypto(id='ETH', name='Ethereum'))

assets = asset_registry.get_all()
pprint(assets)
