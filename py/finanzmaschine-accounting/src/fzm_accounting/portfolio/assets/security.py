from dataclasses import dataclass

from fzm_accounting.portfolio.assets.asset import Asset


@dataclass(frozen=True)
class Security(Asset):
    pass
