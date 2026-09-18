from sqlmodel import Field

from finanzmaschine_staking.orm.near.balance_snapshot import BalanceSnapshot


class StakingSnapshot(BalanceSnapshot, table=True):
    __tablename__ = 'near_staking_snapshots'

    account_key: str = Field(primary_key=True)
    pool_id: str = Field(primary_key=True)
