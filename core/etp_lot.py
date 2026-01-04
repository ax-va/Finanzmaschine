from core.instrument import Instrument
from core.share_lot import ShareLot


class EtpLot(ShareLot):
    def __init__(
        self,
        share_isin: str,
        share_name: str,
        asset_name: str,
    ):
        super().__init__(
            share_isin=share_isin,
            share_name=share_name,
            share_instrument=Instrument.ETP,
            asset_name=asset_name,
        )