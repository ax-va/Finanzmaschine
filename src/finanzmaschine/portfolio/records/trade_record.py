from dataclasses import dataclass
from enum import StrEnum

from finanzmaschine.portfolio.records.priced_record import PricedRecord


class Side(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class TradeRecord(PricedRecord):
    side: Side
