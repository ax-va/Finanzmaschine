from pprint import pprint

from finanzmaschine.catalog import asset_registry

etp = asset_registry.get("GB00BLD4ZM24")
print(etp)
# Etp(id='GB00BLD4ZM24', name='CoinShares Physical Staked Ethereum', underlying_asset=Asset(id='ETH', name='Ethereum'))

assets = asset_registry.get_all()
pprint(assets)
# [Asset(id='BTC', name='Bitcoin'),
#  Asset(id='ETH', name='Ethereum'),
#  Asset(id='NEAR', name='NEAR Protocol'),
#  Asset(id='SOL', name='Solana'),
#  Asset(id='TON', name='Toncoin'),
#  Asset(id='EUR', name='Euro'),
#  Asset(id='USD', name='United States Dollar'),
#  Etp(id='GB00BLD4ZM24',
#      name='CoinShares Physical Staked Ethereum',
#      underlying_asset=Asset(id='ETH', name='Ethereum')),
#  Etp(id='CH1297762812',
#      name='21Shares Toncoin Staking ETP',
#      underlying_asset=Asset(id='TON', name='Toncoin'))]
