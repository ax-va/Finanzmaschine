from fzm_near.orm.staking.balance import Balance
from fzm_near.orm.staking.key import Key


class Snapshot(
    Key,
    Balance,
    table=True,
):
    """Represents a NEAR staking snapshot."""

    __tablename__ = 'near_staking_snapshots'
