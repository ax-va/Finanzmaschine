from core.etp_lot import ETPLot


class LotGB00BLD4ZM24(ETPLot):
    def __init__(self):
        super().__init__(
            share_isin="GB00BLD4ZM24",
            share_name="CoinShares Physical Staked Ethereum",
            asset_name="ETH",
        )
