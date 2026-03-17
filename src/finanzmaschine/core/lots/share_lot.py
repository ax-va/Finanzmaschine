from datetime import datetime
from decimal import Decimal
from typing import override, Self, Type

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

    lot_record_cls = ShareLotRecord

    def __init__(self, base_asset: Share):
        super().__init__(base_asset)

    @property
    def shared_asset(self) -> Asset:
        return self.base_asset.shared_asset

    @classmethod
    def open(
        cls: Type[Self],
        *,
        base_asset: Share,
        quantity: float,
        price: Decimal,
        quote_asset: Asset,
        fee: Decimal,
        fee_asset: Asset,
        dt: datetime,
        entitlement: float | None = None,
    ) -> Self:
        return super().open(
            base_asset=base_asset,
            quantity=quantity,
            price=price,
            quote_asset=quote_asset,
            fee=fee,
            fee_asset=fee_asset,
            dt=dt,
            entitlement=entitlement,
        )

    @override
    def close_quantity(
        self,
        *,
        quantity: float,
        price: Decimal,
        quote_asset: Asset,
        fee: Decimal,
        fee_asset: Asset,
        dt: datetime,
        entitlement: float | None = None,
    ) -> None:
        super().close_quantity(
            quantity=quantity,
            price=price,
            quote_asset=quote_asset,
            fee=fee,
            fee_asset=fee_asset,
            dt=dt,
            entitlement=entitlement,
        )
