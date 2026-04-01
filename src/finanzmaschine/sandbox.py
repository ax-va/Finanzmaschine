from pprint import pprint

from finanzmaschine.catalog.asset_registry import asset_registry

crypto_etp = asset_registry.get("GB00BLD4ZM24")
print(crypto_etp)
# CryptoEtp(id='GB00BLD4ZM24', name='CoinShares Physical Staked Ethereum', underlying_asset=Crypto(id='ETH', name='Ethereum'))

assets = asset_registry.get_all()
pprint(assets)
