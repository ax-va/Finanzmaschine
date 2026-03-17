from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from finanzmaschine.catalog.asset_enum import Asset


@dataclass(frozen=True)
class BaseLotRecord:
    quantity: float
    price: Decimal
    quote_asset: Asset
    fee: Decimal
    fee_asset: Asset
    dt: datetime
