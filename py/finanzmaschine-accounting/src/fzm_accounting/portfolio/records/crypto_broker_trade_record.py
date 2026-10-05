from dataclasses import dataclass

from fzm_accounting.portfolio.assets import Crypto
from fzm_accounting.portfolio.records.mixins.broker_order_mixin import BrokerOrderMixin
from fzm_accounting.portfolio.records.mixins.counterparty_mixin import CounterpartyMixin
from fzm_accounting.portfolio.records.trade_record import TradeRecord


@dataclass(frozen=True, eq=False, kw_only=True)
class CryptoBrokerTradeRecord(TradeRecord[Crypto], BrokerOrderMixin, CounterpartyMixin):
    pass
