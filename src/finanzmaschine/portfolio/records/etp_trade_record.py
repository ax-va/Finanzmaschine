from dataclasses import dataclass

from finanzmaschine.portfolio.records.security_trade_record import SecurityTradeRecord
from finanzmaschine.portfolio.infos.etp_underlying_asset_info import EtpUnderlyingAssetInfo


@dataclass(frozen=True)
class EtpTradeRecord(SecurityTradeRecord):
    underlying_asset_info: EtpUnderlyingAssetInfo
