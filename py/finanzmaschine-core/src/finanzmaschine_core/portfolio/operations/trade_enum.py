from enum import StrEnum

from finanzmaschine_core.portfolio.operations.direction_enum import DirectionEnum


class TradeEnum(StrEnum):
    BUY = "BUY"
    SELL = "SELL"

    @property
    def direction(self) -> DirectionEnum:
        return {
            TradeEnum.BUY: DirectionEnum.IN,
            TradeEnum.SELL: DirectionEnum.OUT,
        }[self]
