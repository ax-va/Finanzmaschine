from fzm_staking.orm.near.balance import Balance
from fzm_staking.orm.near.key import Key


class Snapshot(
    Key,
    Balance,
    table=True,
):
    __tablename__ = 'near_staking_snapshots'
