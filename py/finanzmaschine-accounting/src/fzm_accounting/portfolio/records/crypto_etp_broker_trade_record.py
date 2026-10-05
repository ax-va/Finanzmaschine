from dataclasses import dataclass

from fzm_accounting.portfolio.assets import CryptoEtp
from fzm_accounting.portfolio.records.mixins.broker_order_mixin import BrokerOrderMixin
from fzm_accounting.portfolio.records.mixins.etp_mixin import EtpMixin
from fzm_accounting.portfolio.records.mixins.exchange_mixin import ExchangeMixin
from fzm_accounting.portfolio.records.trade_record import TradeRecord


@dataclass(frozen=True, eq=False, kw_only=True)
class CryptoEtpBrokerTradeRecord(TradeRecord[CryptoEtp], BrokerOrderMixin, ExchangeMixin, EtpMixin):

    def __post_init__(self):
        TradeRecord.__post_init__(self)
        EtpMixin.__post_init__(self)
