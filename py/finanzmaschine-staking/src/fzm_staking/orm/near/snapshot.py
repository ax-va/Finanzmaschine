from fzm_staking.orm.near.balance import Balance
from fzm_staking.orm.near.snapshot_metadata import SnapshotMetadata


class StakingSnapshot(
    SnapshotMetadata,
    Balance,
    table=True,
):
    __tablename__ = 'near_staking_snapshots'
