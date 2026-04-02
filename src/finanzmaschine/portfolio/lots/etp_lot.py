from typing import TypeVar

from finanzmaschine.portfolio.assets import BaseAsset
from finanzmaschine.portfolio.assets.etp import Etp
from finanzmaschine.portfolio.lots.security_lot import SecurityLot
from finanzmaschine.portfolio.operation_types.non_trade_increase_type import NonTradeIncreaseRecord
from finanzmaschine.portfolio.records.etp_trade_record import EtpTradeRecord
from finanzmaschine.portfolio.records.non_trade_decrease_record import NonTradeDecreaseRecord

E = TypeVar("E", bound="Etp")
U = TypeVar("U", bound=BaseAsset)


class EtpLot(SecurityLot[Etp[E, U], NonTradeDecreaseRecord, EtpTradeRecord, NonTradeIncreaseRecord]):
    """
    A lot corresponding to an ETP instrument.

    Each ETP unit carries an entitlement to an underlying asset:

    underlying_asset_quantity = etp_quantity * entitlement
    underlying_asset_price = etp_price / entitlement
    """

    @property
    def underlying_asset(self) -> U:
        return self.base_asset.underlying_asset
