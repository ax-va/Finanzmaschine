from typing import TypeVar, Generic

from finanzmaschine.portfolio.assets.asset import Asset
from finanzmaschine.portfolio.assets.etp import Etp
from finanzmaschine.portfolio.lots.security_lot import SecurityLot
from finanzmaschine.portfolio.records.etp_trade_record import EtpTradeRecord

E = TypeVar("E", bound=Etp)
T = TypeVar("T", bound=EtpTradeRecord)
U = TypeVar("U", bound=Asset)


class EtpLot(SecurityLot[E, T], Generic[E, T, U]):
    """
    A lot corresponding to an ETP instrument.

    Each ETP unit carries an entitlement to an underlying asset:

    underlying_asset_quantity = etp_quantity * entitlement
    underlying_asset_price = etp_price / entitlement
    """

    @property
    def underlying_asset(self) -> U:
        return self.base_asset.underlying_asset
