from finanzmaschine.portfolio.assets.crypto import Crypto
from finanzmaschine.portfolio.assets.crypto_etp import CryptoEtp
from finanzmaschine.portfolio.lots import EtpLot
from finanzmaschine.portfolio.operation_types.non_trade_increase_type import NonTradeIncreaseType
from finanzmaschine.portfolio.records.crypto_etp_trade_record import CryptoEtpTradeRecord
from finanzmaschine.portfolio.records.non_trade_decrease_record import NonTradeDecreaseRecord
from finanzmaschine.portfolio.records.non_trade_increase_record import NonTradeIncreaseRecord


class CryptoEtpLot(
    EtpLot[
        CryptoEtp,
        NonTradeDecreaseRecord,
        CryptoEtpTradeRecord,
        NonTradeIncreaseRecord[Crypto, NonTradeIncreaseType],
        Crypto,
    ]
):
    pass
