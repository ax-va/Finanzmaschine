from dataclasses import dataclass

from fzm_accounting.portfolio.records.mixins.broker_mixin import BrokerMixin


@dataclass(frozen=True, eq=False, kw_only=True)
class BrokerOrderMixin(BrokerMixin):
    order_id: str
