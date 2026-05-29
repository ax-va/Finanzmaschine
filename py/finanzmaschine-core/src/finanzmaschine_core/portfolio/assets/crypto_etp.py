from dataclasses import dataclass

from finanzmaschine_core.portfolio.assets import Etp
from finanzmaschine_core.portfolio.assets.crypto import Crypto


@dataclass(frozen=True)
class CryptoEtp[C: Crypto](Etp[C]):
    pass