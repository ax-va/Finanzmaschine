from datetime import datetime
from pathlib import Path

import polars as pl
import yaml

from finanzmaschine_staking.orm.near.balance_snapshot import BalanceSnapshot
from finanzmaschine_staking.orm.near.snapshot_metadata import SnapshotMetadata

BLOCK_HEIGHT = "block_height"
STAKED_BALANCE_YOCTO_STR = "staked_balance_yocto_str"
UNSTAKED_BALANCE_YOCTO_STR = "unstaked_balance_yocto_str"


class SnapshotStorage:
    """
    Stores metadata and balance snapshots that are collected during a staking balance search.

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
        self._df_balance_snapshots = pl.DataFrame(schema=self.SCHEMA)

        if target_dir is not None:
            self._target_dir = Path(target_dir)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            self._target_dir = Path.cwd() / f"snapshots_{timestamp}"

        self._target_dir.mkdir(parents=True, exist_ok=True)
        self._metadata_path = self._target_dir / "near_metadata.yaml"

    @property
    def metadata(self) -> SnapshotMetadata:
        return self._metadata

    @property
    def df_balance_snapshots(self) -> pl.DataFrame:
        return self._df_balance_snapshots

    def add(
        self,
        snapshot: BalanceSnapshot,
    ) -> None:
        df_duplicates: pl.DataFrame = self._df_balance_snapshots.filter(
            (pl.col(BLOCK_HEIGHT) == snapshot.block_height)
        )

        if not df_duplicates.is_empty():
            raise ValueError(
                f"Snapshot already exists for {BLOCK_HEIGHT}={snapshot.block_height}"
            )

        df_row = pl.DataFrame(
            {
                BLOCK_HEIGHT: [snapshot.block_height],
                STAKED_BALANCE_YOCTO_STR: [snapshot.staked_balance_yocto_str],
                UNSTAKED_BALANCE_YOCTO_STR: [snapshot.unstaked_balance_yocto_str],
            },
            schema=self.SCHEMA,
        )

        self._df_balance_snapshots: pl.DataFrame = (
            pl.concat([self._df_balance_snapshots, df_row])
            .sort([BLOCK_HEIGHT])
        )

    def get(
        self,
        block_height: int,
    ) -> BalanceSnapshot | None:
        df_snapshot: pl.DataFrame = self._df_balance_snapshots.filter(
            (pl.col(BLOCK_HEIGHT) == block_height)
        )

        if df_snapshot.is_empty():
            return None

        if df_snapshot.height > 1:
            raise RuntimeError(
                f"Multiple snapshots found for {BLOCK_HEIGHT}={block_height}"
            )

        row: dict = df_snapshot.row(0, named=True)

        return BalanceSnapshot(
            block_height=row[BLOCK_HEIGHT],
            staked_balance_yocto_str=row[STAKED_BALANCE_YOCTO_STR],
            unstaked_balance_yocto_str=row[UNSTAKED_BALANCE_YOCTO_STR],
        )

    def clear(self) -> None:
        self._df_balance_snapshots = pl.DataFrame(schema=self.SCHEMA)

    def save(self) -> None:
        self._save_metadata()
        self._save_balance_snapshots()

    def _save_metadata(self) -> None:
        if not self._metadata_path.exists():
            with self._metadata_path.open("w") as f:
                yaml.safe_dump(self._metadata.model_dump(), f)

    def _save_balance_snapshots(self) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        file_stem = (
            self._target_dir / f"near_balance_snapshots_{timestamp}"
        )

        self._df_balance_snapshots.write_csv(
            file_stem.with_suffix(".csv")
        )
        self._df_balance_snapshots.write_parquet(
            file_stem.with_suffix(".parquet")
        )
