from dataclasses import dataclass
from datetime import datetime
from typing import Self


@dataclass
class DatetimeInterval:
    dt_lower: datetime
    dt_upper: datetime
    
    def __lt__(self, other: datetime | Self) -> bool:
        if isinstance(other, datetime):
            return self.dt_upper < other
        if isinstance(other, DatetimeInterval):
            return self.dt_upper < other.dt_lower
        raise TypeError(f"The `other` instance is not of type `datetime` or `{type(self).__name__}`")
    
    def __gt__(self, other: datetime | Self) -> bool:
        if isinstance(other, datetime):
            return self.dt_lower > other
        if isinstance(other, DatetimeInterval):
            return self.dt_lower > other.dt_upper
        raise TypeError(f"The `other` instance is not of type `datetime` or `{type(self).__name__}`")
    
    def __le__(self, other: datetime | Self) -> bool:
        if isinstance(other, datetime):
            return self.dt_upper <= other
        if isinstance(other, DatetimeInterval):
            return self.dt_upper <= other.dt_lower
        raise TypeError(f"The `other` instance is not of type `datetime` or `{type(self).__name__}`")
    
    def __ge__(self, other: datetime | Self) -> bool:
        if isinstance(other, datetime):
            return self.dt_lower >= other
        if isinstance(other, DatetimeInterval):
            return self.dt_lower >= other.dt_upper
        raise TypeError(f"The `other` instance is not of type `datetime` or `{type(self).__name__}`")
    
    def __eq__(self, other: Self) -> bool:
        if isinstance(other, DatetimeInterval):
            return self.dt_lower == other.dt_lower and self.dt_upper == other.dt_upper
        raise TypeError(f"The `other` instance is not of type `{type(self).__name__}`")
    
    def __ne__(self, other: Self) -> bool:
        return  not (self == other)
    
    def __contains__(self, dt: datetime) -> bool:
        if isinstance(dt, datetime):
            return self.dt_lower <= dt <= self.dt_upper
        raise TypeError("The `dt` instance is not of type `datetime`")
