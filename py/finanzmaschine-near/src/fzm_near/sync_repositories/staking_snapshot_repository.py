import logging
from pathlib import Path

import polars as pl
from sqlalchemy import Integer, func, type_coerce
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from fzm_near.orm.staking_key import StakingKey
from fzm_near.orm.staking_snapshot import StakingSnapshot
from fzm_near.staking.dataframes import load_key, load_df_balances, create_df_staking_snapshots

logger = logging.getLogger(__name__)


class StakingSnapshotRepository:
    """Provides synchronous database operations for NEAR staking snapshots."""

    def __init__(self, session: Session) -> None:
        """
        Args:
            session: Database session used for persistence operations.
        """
        self._session = session

    @property
    def session(self) -> Session:
        """Returns the database session used by the repository."""
        return self._session

    def get(
        self,
        key: StakingKey,
        block_height: int,
    ) -> StakingSnapshot | None:
        """
        Returns a staking snapshot by its snapshot key and block height.

        Args:
            key: Staking relationship key.
            block_height: Block height of the staking snapshot.

        Returns:
            The staking snapshot or `None` if it does not exist.
        """
        return self._session.get(
            StakingSnapshot,
            (key.account_key, key.pool_key, block_height),
        )

    def get_latest(self, key: StakingKey) -> StakingSnapshot | None:
        """
        Returns the latest staking snapshot for a key.

        Args:
            key: Staking relationship key.

        Returns:
            The snapshot with the greatest block height,
            or `None` if none exists.
        """
        statement = select(
            type_coerce(
                func.max(StakingSnapshot.block_height),
                Integer,
            )
        ).where(
            StakingSnapshot.account_key == key.account_key,
            StakingSnapshot.pool_key == key.pool_key,
        )

        block_height: int | None = self._session.exec(statement).one()

        if block_height is None:
            return None

        return self.get(key, block_height)


    def add(self, snapshot: StakingSnapshot) -> None:
        """
        Adds a staking snapshot to the current database session.

        Args:
            snapshot: Staking snapshot to add.
        """
        self._session.add(snapshot)

    def flush(self) -> None:
        """Flushes pending changes to the database."""
        self._session.flush()

    def safe_add(self, snapshot: StakingSnapshot) -> bool:
        """
        Adds and flushes a staking snapshot within a savepoint.

        If an integrity conflict occurs,
        the savepoint is rolled back
        without rolling back the surrounding transaction.

        Args:
            snapshot: Staking snapshot to add.

        Returns:
            `True` if the staking snapshot was successfully flushed, otherwise `False`.
        """
        try:
            with self._session.begin_nested():
                # savepoint
                self.add(snapshot)
                self.flush()

            return True

        except IntegrityError:
            return False

    def import_from(
        self,
        source_dir: str | Path,
    ) -> None:
        """
        Imports staking snapshots from the given directory to the database.

        Loads snapshot key from `key.yaml` in `source_dir`
        and processes all CSV files in the directory.

        For each balance snapshot, ensures that
        the corresponding block exists in the database
        before importing the staking snapshot.

        Snapshots that cause an integrity conflict are not imported.

        Args:
            source_dir:
                Directory containing staking `key.yaml` and balance snapshot CSV files.
        """

        logger.info("Starting staking snapshots import to the database")

        source_dir = Path(source_dir)

        logger.info(f"From source directory: {source_dir}")

        key: StakingKey = load_key(source_dir / "key.yaml")

        logger.info(f"Loaded account key: {key.account_key}")
        logger.info(f"Loaded pool key: {key.pool_key}")

        csv_paths: list[Path] = sorted(source_dir.glob("*.csv"))
        num_csv_paths: int = len(csv_paths)

        logger.info(f"Found {num_csv_paths} CSV files")

        for index, csv_path in enumerate(csv_paths, start=1):
            logger.info(
                f"Importing balance snapshots {index}/{num_csv_paths}: {csv_path.name}"
            )

            df_balances: pl.DataFrame = load_df_balances(csv_path)

            logger.debug(f"Loaded {df_balances.height} balance snapshots")

            imported_snapshots_count: int = self._import(
                key=key,
                df_balances=df_balances,
            )

            logger.debug(f"Imported {imported_snapshots_count} staking snapshots")

        logger.info(f"Processed {num_csv_paths} staking snapshot files")

    def _import(
        self,
        key: StakingKey,
        df_balances: pl.DataFrame,
    ) -> int:
        """
        Imports staking snapshots into the database.

        Snapshots that cause an integrity conflict are not imported.

        Args:
            key: Snapshot key containing the account and pool keys.
            df_balances: Dataframe containing balance snapshots to import.

        Returns:
            The number of staking snapshots successfully imported.
        """

        logger.debug("Importing staking snapshots to the database")

        imported_count: int = 0

        df_staking_snapshots: pl.DataFrame = create_df_staking_snapshots(
            key=key,
            df_balances=df_balances,
        )

        for row in df_staking_snapshots.iter_rows(named=True):
            snapshot: StakingSnapshot = StakingSnapshot.model_validate(row)

            if self.safe_add(snapshot):
                imported_count += 1
                logger.debug(
                    f"Imported staking snapshot at block {snapshot.block_height}"
                )
            else:
                logger.debug(
                    f"Staking snapshot at block height {snapshot.block_height} "
                    f"was not inserted due to an integrity conflict"
                )

        return imported_count
