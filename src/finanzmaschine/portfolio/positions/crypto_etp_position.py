from finanzmaschine.portfolio.assets.crypto_etp import CryptoEtp
from finanzmaschine.portfolio.lots.crypto_etp_lot import CryptoEtpLot
from finanzmaschine.portfolio.positions.etp_position import EtpPosition
from finanzmaschine.portfolio.records.non_trade_increase_record import NonTradeIncreaseRecord
from finanzmaschine.portfolio.records.crypto_etp_trade_record import CryptoEtpTradeRecord

RecordIn = NonTradeIncreaseRecord | CryptoEtpTradeRecord


class CryptoEtpPosition(
    EtpPosition[
        CryptoEtp,
        CryptoEtpTradeRecord,
        CryptoEtpLot,
    ]
):
    def _create_lot(self, record_in: RecordIn) -> CryptoEtpLot:
        return CryptoEtpLot(base_asset=self.base_asset, record_in=record_in)
