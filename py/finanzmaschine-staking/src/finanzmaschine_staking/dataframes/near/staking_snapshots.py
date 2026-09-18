from pathlib import Path

import polars as pl

from finanzmaschine_staking.dataframes.near.balance_snapshots import (
    SCHEMA,
    BLOCK_HEIGHT,
    STAKED_BALANCE_YOCTO_STR,
    UNSTAKED_BALANCE_YOCTO_STR,
)

ACCOUNT_KEY = "ACCOUNT_KEY"
POOL_ID = "POOL_ID"


def load_snapshots(parquet_path: str | Path) -> pl.DataFrame:
    return pl.read_parquet(parquet_path)


def create_snapshots(
    account_key: str,
    pool_id: str,
    df: pl.DataFrame,
) -> pl.DataFrame:

    # Validate schema
    if not all(
        df.schema.get(column) == dtype
        for column, dtype in SCHEMA.items()
    ):
        raise ValueError(
            f"Expected schema to contain {SCHEMA}, got {df.schema}"
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
