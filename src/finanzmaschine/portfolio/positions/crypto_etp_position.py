from finanzmaschine.portfolio.assets.crypto_etp import CryptoEtp
from finanzmaschine.portfolio.lots.crypto_etp_lot import CryptoEtpLot
from finanzmaschine.portfolio.positions.etp_position import EtpPosition
from finanzmaschine.portfolio.records.crypto_etp_trade_record import CryptoEtpTradeRecord
from finanzmaschine.portfolio.records.non_trade_decrease_record import NonTradeDecreaseRecord
from finanzmaschine.portfolio.records.non_trade_increase_record import NonTradeIncreaseRecord


class CryptoEtpPosition(
    EtpPosition[CryptoEtp, NonTradeDecreaseRecord, NonTradeIncreaseRecord, CryptoEtpTradeRecord, CryptoEtpLot]
):
    pass