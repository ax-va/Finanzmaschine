from dataclasses import dataclass

from finanzmaschine_accounting.portfolio.assets import Crypto
from finanzmaschine_accounting.portfolio.records.mixins.broker_order_mixin import BrokerOrderMixin
from finanzmaschine_accounting.portfolio.records.mixins.counterparty_mixin import CounterpartyMixin
from finanzmaschine_accounting.portfolio.records.trade_record import TradeRecord


@dataclass(frozen=True, eq=False, kw_only=True)
class CryptoBrokerTradeRecord(TradeRecord[Crypto], BrokerOrderMixin, CounterpartyMixin):
    pass
