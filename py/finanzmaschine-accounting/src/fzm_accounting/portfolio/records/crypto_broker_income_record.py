from dataclasses import dataclass

from fzm_accounting.portfolio.assets import Crypto
from fzm_accounting.portfolio.records.income_record import IncomeRecord
from fzm_accounting.portfolio.records.mixins.broker_mixin import BrokerMixin


@dataclass(frozen=True, eq=False, kw_only=True)
class CryptoBrokerIncomeRecord(IncomeRecord[Crypto], BrokerMixin):
    pass
