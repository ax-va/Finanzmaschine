from pathlib import Path

import polars as pl
import yaml

from fzm_staking.storage.near.snapshot_storage import (
    BLOCK_HEIGHT,
    STAKED_BALANCE_YOCTO_STR,
    UNSTAKED_BALANCE_YOCTO_STR,
    ACCOUNT_KEY,
    POOL_KEY,
    SnapshotStorage,
)
from fzm_staking.orm.near.snapshot_metadata import SnapshotMetadata

STAKING_SNAPSHOT_SCHEMA = {
    ACCOUNT_KEY: pl.String,
    POOL_KEY: pl.String,
    **SnapshotStorage.SCHEMA,
}


def load_df_balances(file_path: str | Path) -> pl.DataFrame:
    """
    Loads balance snapshots from a CSV file.

    Args:
        file_path: Path to CSV file containing balance snapshots.

    Returns:
        A dataframe containing the loaded balance snapshots.
    """
    return pl.read_csv(
        file_path,
        schema_overrides=SnapshotStorage.SCHEMA,
    )


def load_snapshot_metadata(file_path: str | Path) -> SnapshotMetadata:
    """
    Loads staking snapshot metadata from a YAML file.

    Args:
        file_path: Path to the YAML file containing snapshot metadata.

    Returns:
        A snapshot metadata object.
    """
    with Path(file_path).open("r", encoding="utf-8") as file:
        return SnapshotMetadata.model_validate(yaml.safe_load(file))


def create_df_staking_snapshots(
    metadata: SnapshotMetadata,
    df_balances: pl.DataFrame,
) -> pl.DataFrame:
    """
    Creates staking snapshots dataframe from metadata and balance snapshots.

    Adds the account and pool keys from metadata to each balance snapshot.

    If `df_balances` is empty, returns
    an empty dataframe with the staking snapshot schema.

    Args:
        metadata: SnapshotMetadata object containing account and pool keys.
        df_balances: Dataframe containing balance snapshots.

    Returns:
        A dataframe containing staking snapshots.

    Raises:
        ValueError:
            If `df_balances` does not contain the columns
            and data types defined by `SnapshotStorage.SCHEMA`.
    """

    # Validate schema
    if not all(
        df_balances.schema.get(column) == dtype
        for column, dtype in SnapshotStorage.SCHEMA.items()
    ):
        raise ValueError(
            f"Expected schema to contain {SnapshotStorage.SCHEMA}, "
            f"got {df_balances.schema}"
        )

    if df_balances.is_empty():
        return pl.DataFrame(schema=STAKING_SNAPSHOT_SCHEMA)

    return pl.DataFrame(
        data={
            ACCOUNT_KEY: metadata.account_key,
            POOL_KEY: metadata.pool_key,
            BLOCK_HEIGHT: df_balances[BLOCK_HEIGHT],
            STAKED_BALANCE_YOCTO_STR: df_balances[STAKED_BALANCE_YOCTO_STR],
            UNSTAKED_BALANCE_YOCTO_STR: df_balances[UNSTAKED_BALANCE_YOCTO_STR],
        },
        schema=SnapshotStorage.SCHEMA,
    )
