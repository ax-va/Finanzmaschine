from dataclasses import dataclass
from typing import TypeVar

from finanzmaschine.portfolio.assets.asset import Asset
from finanzmaschine.portfolio.operation_types.trade_type import TradeType
from finanzmaschine.portfolio.records.priced_record import PricedRecord

Q = TypeVar("Q", bound=Asset)
O = TypeVar("O", bound=TradeType)


@dataclass(frozen=True)
class TradeRecord(PricedRecord[Q, O]):
    pass
