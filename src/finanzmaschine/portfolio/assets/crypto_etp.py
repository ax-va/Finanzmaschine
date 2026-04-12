from dataclasses import dataclass

from finanzmaschine.portfolio.assets import Etp
from finanzmaschine.portfolio.assets.crypto import Crypto


@dataclass(frozen=True)
class CryptoEtp[C: Crypto](Etp[C]):
    pass