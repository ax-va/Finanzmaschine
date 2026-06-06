from finanzmaschine_core.portfolio.operations.base_operation_enum import BaseOperationEnum
from finanzmaschine_core.portfolio.operations.direction_enum import DirectionEnum


class IncomeEnum(BaseOperationEnum):
    STAKING = "STAKING"

    @property
    def direction(self) -> DirectionEnum:
        return {
            IncomeEnum.STAKING: DirectionEnum.IN,
        }[self]
