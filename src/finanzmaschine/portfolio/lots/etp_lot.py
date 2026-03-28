from finanzmaschine.portfolio.assets import BaseAsset
from finanzmaschine.portfolio.trade_infos.etp_trade_info import EtpRecord
from finanzmaschine.portfolio.assets.etp import Etp
from finanzmaschine.portfolio.lots.security_lot import SecurityLot


class EtpLot[A: BaseAsset](SecurityLot[Etp, EtpRecord]):
    """
    A lot corresponding to an ETP instrument.

    Each ETP unit carries an entitlement to an underlying asset:

    underlying_asset_quantity = etp_quantity * entitlement
    underlying_asset_price = etp_price / entitlement
    """

    def __init__(self, base_asset: Etp, record_in: EtpRecord) -> None:
        super().__init__(base_asset, record_in)

    @property
    def underlying_asset(self) -> A:
        return self.base_asset.underlying_asset
