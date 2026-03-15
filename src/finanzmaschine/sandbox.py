from pprint import pprint

from finanzmaschine.catalog import registry
from finanzmaschine.catalog.asset_enum import Asset

instrument = registry.get_by_isin("GB00BLD4ZM24")
print(instrument)
# Share(isin='GB00BLD4ZM24', name='CoinShares Physical Staked Ethereum', asset=<Asset.ETH: 'ETH'>)

instrument = registry.get_by_asset(Asset.ETH)
pprint(instrument)
# [Share(isin='GB00BLD4ZM24',
#        name='CoinShares Physical Staked Ethereum',
#        asset=<Asset.ETH: 'ETH'>)]

shares = registry.get_all_shares()
pprint(shares)
# [Share(isin='GB00BLD4ZM24',
#        name='CoinShares Physical Staked Ethereum',
#        asset=<Asset.ETH: 'ETH'>),
#  Share(isin='CH1297762812',
#        name='21Shares Toncoin Staking ETP',
#        asset=<Asset.TON: 'TON'>)]
