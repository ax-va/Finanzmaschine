import datetime
import math
from typing import List


class BaseLot:
    def __init__(self):
        self.units_in: float = 0
        self.price_in: float | None = None
        self.datetime_in: datetime.datetime | None = None
        self.units_out_list: List[float] = []
        self.price_out_list: List[float] = []
        self.datetime_out_list: List[datetime.datetime] = []

    @property
    def units_out_total(self):
        return math.fsum(self.units_out_list)

    @property
    def units_open(self) -> float:
        return self.units_in - self.units_out_total
