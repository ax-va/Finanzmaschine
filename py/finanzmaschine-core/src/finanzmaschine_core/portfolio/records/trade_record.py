from dataclasses import dataclass

from finanzmaschine_core.portfolio.assets.asset import Asset
from finanzmaschine_core.portfolio.operation_types.trade_type import TradeType
from finanzmaschine_core.portfolio.records.priced_record import PricedRecord


@dataclass(frozen=True, eq=False)
class TradeRecord[Q: Asset, T: TradeType](PricedRecord[Q, T]):
    pass
