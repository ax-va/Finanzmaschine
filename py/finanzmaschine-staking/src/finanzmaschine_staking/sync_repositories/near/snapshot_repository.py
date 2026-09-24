import polars as pl
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from finanzmaschine_staking.orm.near.staking_snapshot import StakingSnapshot


class SnapshotRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

    def get(
        self,
        block_height: int,
        account_key: str,
        pool_id: str,
    ) -> StakingSnapshot | None:
        return self._session.get(
            StakingSnapshot,
            (account_key, pool_id, block_height),
        )

    def add(self, snapshot: StakingSnapshot) -> None:
        self._session.add(snapshot)

    def add_all(self, df: pl.DataFrame) -> None:
        self._session.connection().execute(
            insert(StakingSnapshot),
            df.to_dicts(),
        )

    def flush(self) -> None:
        self._session.flush()

    def safe_add(self, snapshot: StakingSnapshot) -> bool:
        try:
            with self._session.begin_nested():
                # savepoint
                self.add(snapshot)
                self.flush()

            return True

        except IntegrityError:
            return False
