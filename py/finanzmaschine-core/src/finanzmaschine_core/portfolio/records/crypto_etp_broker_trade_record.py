from dataclasses import dataclass

from finanzmaschine_core.portfolio.assets import CryptoEtp
from finanzmaschine_core.portfolio.records.mixins.broker_order_mixin import BrokerOrderMixin
from finanzmaschine_core.portfolio.records.mixins.etp_mixin import EtpMixin
from finanzmaschine_core.portfolio.records.mixins.exchange_mixin import ExchangeMixin
from finanzmaschine_core.portfolio.records.trade_record import TradeRecord


@dataclass(frozen=True, eq=False, kw_only=True)
class CryptoEtpBrokerTradeRecord(TradeRecord[CryptoEtp], BrokerOrderMixin, ExchangeMixin, EtpMixin):

    def __post_init__(self):
        TradeRecord.__post_init__(self)
        EtpMixin.__post_init__(self)
