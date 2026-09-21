import polars as pl
from sqlalchemy import insert
from sqlmodel import Session

from finanzmaschine_staking.orm.near.staking_snapshot import StakingSnapshot


class SnapshotRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(
        self,
        block_height: int,
        account_key: str,
        pool_id: str,
    ) -> StakingSnapshot | None:
        return self._session.get(
            StakingSnapshot,
            (block_height, account_key, pool_id),
        )

    def add(self, snapshot: StakingSnapshot) -> None:
        self._session.add(snapshot)

    def add_all(self, df: pl.DataFrame) -> None:
        self._session.connection().execute(
            insert(StakingSnapshot),
            df.to_dicts(),
        )
