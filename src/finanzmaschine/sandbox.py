from pprint import pprint

from finanzmaschine.catalog.asset_registry import asset_registry

eth_etp = asset_registry.get("GB00BLD4ZM24")
pprint(eth_etp)
# CryptoEtp(id='GB00BLD4ZM24',
#           name='CoinShares Physical Staked Ethereum',
#           quantum='1e-8',
#           underlying_asset=Crypto(id='ETH', name='Ethereum', quantum='1e-18'))

ts_ton = asset_registry.get("tsTON")
pprint(ts_ton)
# LiquidStakingToken(id='tsTON',
#                    name='Tonstakers TON',
#                    quantum='1e-9',
#                    underlying_asset=Crypto(id='TON',
#                                            name='Toncoin',
#                                            quantum='1e-9'))

assets = asset_registry.get_all()
pprint(assets)
