from dataclasses import dataclass

from fzm_accounting.portfolio.assets import Etp
from fzm_accounting.portfolio.assets.crypto import Crypto


@dataclass(frozen=True)
class CryptoEtp[C: Crypto](Etp[C]):
    pass