from finanzmaschine.portfolio.assets.crypto import Crypto
from finanzmaschine.portfolio.assets.crypto_etp import CryptoEtp
from finanzmaschine.portfolio.lots import EtpLot
from finanzmaschine.portfolio.records.crypto_etp_trade_record import CryptoEtpTradeRecord


class CryptoEtpLot(
    EtpLot[
        CryptoEtp,
        CryptoEtpTradeRecord,
        Crypto,
    ]
):
    pass
