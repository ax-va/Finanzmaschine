from dataclasses import dataclass

from finanzmaschine_core.portfolio.assets import Crypto


@dataclass(frozen=True)
class LiquidStakingToken[C: Crypto](Crypto):
    underlying_asset: C
