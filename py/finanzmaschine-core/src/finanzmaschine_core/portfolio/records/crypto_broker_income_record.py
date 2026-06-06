from dataclasses import dataclass

from finanzmaschine_core.portfolio.assets import Crypto
from finanzmaschine_core.portfolio.records.income_record import IncomeRecord
from finanzmaschine_core.portfolio.records.mixins.broker_mixin import BrokerMixin


@dataclass(frozen=True, eq=False, kw_only=True)
class CryptoBrokerIncomeRecord(IncomeRecord[Crypto], BrokerMixin):
    pass
