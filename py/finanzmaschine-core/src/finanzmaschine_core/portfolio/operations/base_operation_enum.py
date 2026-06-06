from enum import StrEnum

from finanzmaschine_core.portfolio.operations.direction_enum import DirectionEnum


class BaseOperationEnum(StrEnum):
    """Base enum class for all portfolio operation enumerations"""

    @property
    def direction(self) -> DirectionEnum:
        raise NotImplementedError("The direction property must be implemented")
