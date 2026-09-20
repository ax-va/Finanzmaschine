from pathlib import Path

import polars as pl
import yaml

from finanzmaschine_staking.dataframes.near.snapshot_storage import (
    BLOCK_HEIGHT,
    STAKED_BALANCE_YOCTO_STR,
    UNSTAKED_BALANCE_YOCTO_STR,
    SnapshotStorage,
)
from finanzmaschine_staking.orm.near.snapshot_metadata import SnapshotMetadata

ACCOUNT_KEY = "account_key"
POOL_ID = "pool_id"


def load_snapshots(file_path: str | Path) -> pl.DataFrame:
    return pl.read_parquet(file_path)


def load_metadata(file_path: str | Path) -> SnapshotMetadata:
    with Path(file_path).open() as f:
        return SnapshotMetadata.model_validate(yaml.safe_load(f))


def create_snapshots(
    account_key: str,
    pool_id: str,
    df: pl.DataFrame,
) -> pl.DataFrame:

    # Validate schema
    if not all(
        df.schema.get(column) == dtype
        for column, dtype in SnapshotStorage.SCHEMA.items()
    ):
        raise ValueError(
            f"Expected schema to contain {SnapshotStorage.SCHEMA}, got {df.schema}"
        )

    return pl.DataFrame(
        data={
            ACCOUNT_KEY: account_key,
            POOL_ID: pool_id,
            BLOCK_HEIGHT: df[BLOCK_HEIGHT],
            STAKED_BALANCE_YOCTO_STR: df[STAKED_BALANCE_YOCTO_STR],
            UNSTAKED_BALANCE_YOCTO_STR: df[UNSTAKED_BALANCE_YOCTO_STR],
        }
    )
