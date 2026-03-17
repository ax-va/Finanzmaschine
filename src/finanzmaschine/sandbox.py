from pprint import pprint

from finanzmaschine.catalog import registry

security = registry.get_by_isin("GB00BLD4ZM24")
print(security)
# Etp(name='CoinShares Physical Staked Ethereum"', isin='GB00BLD4ZM24', underlying=<Asset.ETH: 'ETH'>)

securities = registry.get_all()
pprint(securities)
# [Etp(name='CoinShares Physical Staked Ethereum',
#      isin='GB00BLD4ZM24',
#      underlying=<Asset.ETH: 'ETH'>),
#  Etp(name='21Shares Toncoin Staking ETP',
#      isin='CH1297762812',
#      underlying=<Asset.TON: 'TON'>)]
