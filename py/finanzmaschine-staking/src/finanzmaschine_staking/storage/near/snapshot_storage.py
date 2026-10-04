import logging
from datetime import datetime
from pathlib import Path

import polars as pl
import yaml

from finanzmaschine_staking.orm.near.balance import Balance
from finanzmaschine_staking.orm.near.snapshot_metadata import SnapshotMetadata

BLOCK_HEIGHT = "block_height"
STAKED_BALANCE_YOCTO_STR = "staked_balance_yocto_str"
UNSTAKED_BALANCE_YOCTO_STR = "unstaked_balance_yocto_str"

logger = logging.getLogger(__name__)


class SnapshotStorage:
    """
    Stores metadata and balance snapshots
    that are collected during a staking balance search.

    Acts as temporary storage between search iterations
    and allows collected snapshots to be retrieved, cleared, and persisted.
    """

    SCHEMA = {
        BLOCK_HEIGHT: pl.Int64,
        STAKED_BALANCE_YOCTO_STR: pl.String,
        UNSTAKED_BALANCE_YOCTO_STR: pl.String,
    }

    def __init__(
        self,
        metadata: SnapshotMetadata,
        target_dir: str | Path | None = None,
    ) -> None:
        """
        Args:
            metadata:
                A metadata object containing an account key and a pool ID.
            target_dir:
                Directory where metadata and balance snapshots from completed chunks are saved.
                If omitted, a timestamped subdirectory is created in the current working directory.
        """
        self._metadata: SnapshotMetadata = metadata
        self._df_balances = pl.DataFrame(schema=self.SCHEMA)

        if target_dir is not None:
            self._target_dir = Path(target_dir)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            self._target_dir = Path.cwd() / f"balances_{timestamp}"

        self._target_dir.mkdir(parents=True, exist_ok=True)

    @property
    def metadata(self) -> SnapshotMetadata:
        return self._metadata

    @property
    def df_balances(self) -> pl.DataFrame:
        return self._df_balances

    def add(
        self,
        balance: Balance,
    ) -> None:
        df_duplicates: pl.DataFrame = self._df_balances.filter(
            (pl.col(BLOCK_HEIGHT) == balance.block_height)
        )

        if not df_duplicates.is_empty():
            raise ValueError(
                f"Snapshot already exists for {BLOCK_HEIGHT}={balance.block_height}"
            )

        df_row = pl.DataFrame(
            {
                BLOCK_HEIGHT: [balance.block_height],
                STAKED_BALANCE_YOCTO_STR: [balance.staked_balance_yocto_str],
                UNSTAKED_BALANCE_YOCTO_STR: [balance.unstaked_balance_yocto_str],
            },
            schema=self.SCHEMA,
        )

        self._df_balances: pl.DataFrame = (
            pl.concat([self._df_balances, df_row])
            .sort([BLOCK_HEIGHT])
        )

    def get(
        self,
        block_height: int,
    ) -> Balance | None:
        df_balance: pl.DataFrame = self._df_balances.filter(
            (pl.col(BLOCK_HEIGHT) == block_height)
        )

        if df_balance.is_empty():
            return None

        if df_balance.height > 1:
            raise RuntimeError(
                f"Multiple snapshots found for {BLOCK_HEIGHT}={block_height}"
            )

        row: dict = df_balance.row(0, named=True)

        return Balance(
            block_height=row[BLOCK_HEIGHT],
            staked_balance_yocto_str=row[STAKED_BALANCE_YOCTO_STR],
            unstaked_balance_yocto_str=row[UNSTAKED_BALANCE_YOCTO_STR],
        )

    def clear(self) -> None:
        self._df_balances = pl.DataFrame(schema=self.SCHEMA)

    def save(
        self,
        lower_block_height: int,
        upper_block_height: int,
    ) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        metadata_path = self._target_dir / f"near_metadata_{timestamp}.yaml"
        with metadata_path.open("w") as f:

            logger.debug(f"Saving metadata in YAML: {metadata_path}")

            yaml.safe_dump(self._metadata.model_dump(), f)

        interval_path = self._target_dir / f"near_interval_{timestamp}.yaml"
        with interval_path.open("w") as f:

            logger.debug(f"Saving interval in YAML: {interval_path}")

            yaml.safe_dump(
                {
                    "lower_block_height": lower_block_height,
                    "upper_block_height": upper_block_height,
                }, f
            )

        balances_file_stem = self._target_dir / f"near_balances_{timestamp}"
        balances_path_csv = balances_file_stem.with_suffix(".csv")
        balances_path_parquet = balances_file_stem.with_suffix(".parquet")

        logger.debug(f"Saving balances in CSV: {balances_path_csv}")

        self._df_balances.write_csv(balances_path_csv)

        logger.debug(f"Saving balances in PARQUET: {balances_path_parquet}")

        self._df_balances.write_parquet(balances_path_parquet)
