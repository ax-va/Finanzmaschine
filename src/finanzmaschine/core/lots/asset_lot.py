from finanzmaschine.core.lots.base_lot import BaseLot
from finanzmaschine.catalog.asset import Asset


class AssetLot(BaseLot):
    """
    A lot representing exposure to an underlying asset.

    Unit balance is not invariant and may change over time due to
    entitlement adjustments, fees, or asset-specific mechanics.

    The number of asset units is defined by the formula:
    asset_units = share_units * entitlement,
    where entitlement is a time-dependent mapping that determines
    how many asset units are represented by a single share unit.
    """

    def __init__(self, asset: Asset):
        super().__init__()
        self.asset: Asset = asset
