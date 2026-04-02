from dataclasses import dataclass
from enum import StrEnum
from typing import TypeVar

from finanzmaschine.portfolio.assets import BaseAsset
from finanzmaschine.portfolio.records.base_record import BaseOperationType
from finanzmaschine.portfolio.records.priced_record import PricedRecord

A = TypeVar("A", bound=BaseAsset)
O = TypeVar("O", bound="TradeOperationType")


class TradeOperationType(BaseOperationType):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class TradeRecord(PricedRecord[A, O]):
    pass
