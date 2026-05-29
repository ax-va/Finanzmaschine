from finanzmaschine_core.portfolio.assets.crypto import Crypto
from finanzmaschine_core.portfolio.assets.crypto_etp import CryptoEtp
from finanzmaschine_core.portfolio.lots import EtpLot
from finanzmaschine_core.portfolio.records.crypto_etp_trade_record import CryptoEtpTradeRecord


class CryptoEtpLot(
    EtpLot[
        CryptoEtp,
        CryptoEtpTradeRecord,
        Crypto,
    ]
):
    pass
