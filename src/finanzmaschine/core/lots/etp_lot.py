from finanzmaschine.core.assets import BaseAsset
from finanzmaschine.core.records.etp_record import EtpRecord
from finanzmaschine.core.assets.etp import Etp
from finanzmaschine.core.lots.security_lot import SecurityLot


class EtpLot[A: BaseAsset](SecurityLot[Etp, EtpRecord]):
    """
    A lot corresponding to an ETP instrument.

    Each ETP unit carries an entitlement to an underlying asset:

    underlying_quantity = etp_quantity * entitlement
    underlying_price = etp_price / entitlement
    """

    def __init__(self, base_asset: Etp, record_in: EtpRecord) -> None:
        super().__init__(base_asset, record_in)

    @property
    def underlying_asset(self) -> A:
        return self.base_asset.underlying_asset
