from enum import StrEnum

from fzm_accounting.portfolio.operations.direction_enum import DirectionEnum


class IncomeEnum(StrEnum):
    SAVEBACK = "SAVEBACK"
    STAKING = "STAKING"

    @property
    def direction(self) -> DirectionEnum:
        return {
            IncomeEnum.SAVEBACK: DirectionEnum.IN,
            IncomeEnum.STAKING: DirectionEnum.IN,
        }[self]
