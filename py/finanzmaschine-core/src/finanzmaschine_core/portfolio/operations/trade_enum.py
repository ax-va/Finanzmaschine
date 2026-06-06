from finanzmaschine_core.portfolio.operations.base_operation_enum import BaseOperationEnum
from finanzmaschine_core.portfolio.operations.direction_enum import DirectionEnum


class TradeEnum(BaseOperationEnum):
    BUY = "BUY"
    SELL = "SELL"

    @property
    def direction(self) -> DirectionEnum:
        return {
            TradeEnum.BUY: DirectionEnum.IN,
            TradeEnum.SELL: DirectionEnum.OUT,
        }[self]
