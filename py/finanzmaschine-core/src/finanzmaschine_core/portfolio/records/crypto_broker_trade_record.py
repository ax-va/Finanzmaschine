from dataclasses import dataclass

from finanzmaschine_core.portfolio.assets import Crypto
from finanzmaschine_core.portfolio.records.mixins.broker_order_mixin import BrokerOrderMixin
from finanzmaschine_core.portfolio.records.mixins.counterparty_mixin import CounterpartyMixin
from finanzmaschine_core.portfolio.records.trade_record import TradeRecord


@dataclass(frozen=True, eq=False, kw_only=True)
class CryptoBrokerTradeRecord(TradeRecord[Crypto], BrokerOrderMixin, CounterpartyMixin):
    pass
