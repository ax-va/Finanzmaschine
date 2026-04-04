from finanzmaschine.portfolio.assets.crypto_etp import CryptoEtp
from finanzmaschine.portfolio.lots.crypto_etp_lot import CryptoEtpLot
from finanzmaschine.portfolio.positions.etp_position import EtpPosition
from finanzmaschine.portfolio.records.crypto_etp_trade_record import CryptoEtpTradeRecord


class CryptoEtpPosition(
    EtpPosition[CryptoEtp, CryptoEtpTradeRecord, CryptoEtpLot]
):
    pass