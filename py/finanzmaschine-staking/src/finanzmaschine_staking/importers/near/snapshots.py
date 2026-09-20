from pathlib import Path

from finanzmaschine_staking.dataframes.near.staking_snapshots import (
    create_snapshots,
    load_metadata,
    load_snapshots,
)
from finanzmaschine_staking.repositories.near.snapshot_repository import SnapshotRepository


def import_snapshots(
    source_dir: str | Path,
    repository: SnapshotRepository,
) -> None:
    source_dir = Path(source_dir)

    metadata = load_metadata(source_dir / "metadata.yaml")

    for parquet_path in sorted(source_dir.glob("*.parquet")):
        df_snapshots = load_snapshots(parquet_path)

        snapshots = create_snapshots(
            account_key=metadata.account_key,
            pool_id=metadata.pool_id,
            df=df_snapshots,
        )

        repository.add_all(snapshots)
