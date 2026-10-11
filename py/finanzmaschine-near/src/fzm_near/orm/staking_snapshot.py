from fzm_near.orm.staking_balance import StakingBalance
from fzm_near.orm.staking_key import StakingKey


class StakingSnapshot(
    StakingKey,
    StakingBalance,
    table=True,
):
    """Represents a NEAR staking snapshot."""

    __tablename__ = 'near_staking_snapshots'
