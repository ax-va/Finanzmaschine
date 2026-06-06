from dataclasses import dataclass

from finanzmaschine_core.portfolio.assets import Asset
from finanzmaschine_core.portfolio.operations.income_enum import IncomeEnum
from finanzmaschine_core.portfolio.records.base_record import BaseRecord
from finanzmaschine_core.portfolio.records.mixins.price_mixin import PriceMixin


@dataclass(frozen=True, eq=False, kw_only=True)
class IncomeRecord[Q: Asset](BaseRecord[IncomeEnum], PriceMixin[Q]):

    def __post_init__(self) -> None:
        BaseRecord.__post_init__(self)
        PriceMixin.__post_init__(self)
