from pathlib import Path

import polars as pl

from finanzmaschine_staking.dataframes.near.staking_snapshots import (
    create_staking_snapshots,
    load_snapshots_metadata,
    load_balance_snapshots,
)
from finanzmaschine_staking.repositories.near.snapshot_repository import SnapshotRepository


def import_snapshots(
    source_dir: str | Path,
    repository: SnapshotRepository,
) -> None:
    source_dir = Path(source_dir)

    metadata = load_snapshots_metadata(source_dir / "metadata.yaml")

    for parquet_path in sorted(source_dir.glob("*.parquet")):
        df_balance_snapshots: pl.DataFrame = load_balance_snapshots(parquet_path)

        df_staking_snapshots: pl.DataFrame = create_staking_snapshots(
            account_key=metadata.account_key,
            pool_id=metadata.pool_id,
            df_balance_snapshots=df_balance_snapshots,
        )

        repository.add_all(df_staking_snapshots)
