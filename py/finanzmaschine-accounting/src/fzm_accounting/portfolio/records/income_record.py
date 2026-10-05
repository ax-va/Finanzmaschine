from dataclasses import dataclass

from fzm_accounting.portfolio.assets import Asset
from fzm_accounting.portfolio.operations.income_enum import IncomeEnum
from fzm_accounting.portfolio.records.base_record import BaseRecord
from fzm_accounting.portfolio.records.mixins.price_mixin import PriceMixin


@dataclass(frozen=True, eq=False, kw_only=True)
class IncomeRecord[Q: Asset](BaseRecord, PriceMixin[Q]):

    def __post_init__(self) -> None:
        if not isinstance(self.operation.variant, IncomeEnum):
            raise ValueError("Operation variant in `IncomeRecord` must be of the `IncomeEnum` type")

        BaseRecord.__post_init__(self)
        PriceMixin.__post_init__(self)
