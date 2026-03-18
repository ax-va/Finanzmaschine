from finanzmaschine.catalog.asset_enum import Asset
from finanzmaschine.core.lots.base_lot import BaseLot
from finanzmaschine.core.lots.etp_lot_record import EtpLotRecord
from finanzmaschine.core.assets.etp import Etp


class EtpLot(BaseLot[Etp, EtpLotRecord]):
    """
    A lot corresponding to a share-based instrument.

    Each ETP unit carries an entitlement to an underlying asset:

    underlying_quantity = etp_quantity * entitlement
    underlying_price = etp_price / entitlement
    """

    def __init__(self, base_asset: Etp, record_in: EtpLotRecord) -> None:
        super().__init__(base_asset, record_in)

    @property
    def underlying_asset(self) -> Asset:
        return self.base_asset.underlying_asset
