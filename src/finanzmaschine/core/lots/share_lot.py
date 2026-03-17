from finanzmaschine.catalog.asset_enum import Asset
from finanzmaschine.core.lots.base_lot import BaseLot
from finanzmaschine.core.lots.share_lot_record import ShareLotRecord
from finanzmaschine.core.market.share import Share


class ShareLot(BaseLot[ShareLotRecord]):
    """
    A lot corresponding to a share-based instrument.

    Each share unit carries an entitlement to an underlying shared asset:

    shared_asset_quantity = base_asset_quantity * entitlement
    shared_asset_price = price / entitlement
    """

    def __init__(self, base_asset: Share, record_in: ShareLotRecord) -> None:
        super().__init__(base_asset, record_in)

    @property
    def shared_asset(self) -> Asset:
        return self.base_asset.shared_asset
