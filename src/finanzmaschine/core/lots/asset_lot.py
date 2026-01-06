import datetime

from finanzmaschine.core.lots.base_lot import BaseLot
from finanzmaschine.core.lots.base_lot_record import BaseLotRecord
from finanzmaschine.core.market.asset import Asset


class AssetLot(BaseLot[BaseLotRecord]):
    """
    A lot corresponding to an underlying asset.

    Unit balance is not invariant and may change due to
    entitlement adjustments, fees, or asset-specific mechanics.
    """

    record_cls = BaseLotRecord

    def __init__(self, asset: Asset):
        super().__init__()
        self.asset: Asset = asset
