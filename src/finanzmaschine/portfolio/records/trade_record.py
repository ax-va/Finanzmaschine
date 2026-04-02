from dataclasses import dataclass
from typing import TypeVar

from finanzmaschine.portfolio.assets import BaseAsset
from finanzmaschine.portfolio.operation_types.trade_type import TradeType
from finanzmaschine.portfolio.records.priced_record import PricedRecord

A = TypeVar("A", bound=BaseAsset)
O = TypeVar("O", bound="TradeType")


@dataclass(frozen=True)
class TradeRecord(PricedRecord[A, O]):
    pass
