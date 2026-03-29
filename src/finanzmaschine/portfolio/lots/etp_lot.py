from typing import TypeVar

from finanzmaschine.portfolio.assets import BaseAsset
from finanzmaschine.portfolio.assets.etp import Etp
from finanzmaschine.portfolio.lots.security_lot import SecurityLot
from finanzmaschine.portfolio.records.etp_trade_record import EtpTradeRecord
from finanzmaschine.portfolio.records.non_sale_reduction_record import NonSaleReductionRecord

A = TypeVar("A", bound=BaseAsset)


class EtpLot(SecurityLot[Etp[A], NonSaleReductionRecord, EtpTradeRecord]):
    """
    A lot corresponding to an ETP instrument.

    Each ETP unit carries an entitlement to an underlying asset:

    underlying_asset_quantity = etp_quantity * entitlement
    underlying_asset_price = etp_price / entitlement
    """

    def __init__(self, base_asset: Etp[A], record_in: EtpTradeRecord) -> None:
        super().__init__(base_asset, record_in)

    @property
    def underlying_asset(self) -> A:
        return self.base_asset.underlying_asset
