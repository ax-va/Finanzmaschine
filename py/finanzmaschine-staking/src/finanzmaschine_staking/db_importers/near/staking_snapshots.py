from pathlib import Path
from typing import Iterable

import polars as pl

from finanzmaschine_staking.dataframes.near.staking_snapshots import (
    create_staking_snapshots,
    load_snapshots_metadata,
    load_balance_snapshots,
)
from finanzmaschine_staking.orm.near.block import Block
from finanzmaschine_staking.repositories.near.block_repository import BlockRepository
from finanzmaschine_staking.repositories.near.snapshot_repository import SnapshotRepository
from finanzmaschine_staking.storage.near.snapshot_storage import BLOCK_HEIGHT
from finanzmaschine_staking.sync_clients.near.block_client import BlockClient


def import_staking_snapshots(
    source_dir: str | Path,
    block_client: BlockClient,
    block_repository: BlockRepository,
    snapshot_repository: SnapshotRepository,
) -> None:
    source_dir = Path(source_dir)

    metadata = load_snapshots_metadata(source_dir / "near_metadata.yaml")

    for parquet_path in sorted(source_dir.glob("*.parquet")):
        df_balance_snapshots: pl.DataFrame = load_balance_snapshots(parquet_path)

        _import_blocks(
            block_heights=df_balance_snapshots[BLOCK_HEIGHT],
            block_client=block_client,
            block_repository=block_repository,
        )

        _import_staking_snapshots(
            account_key=metadata.account_key,
            pool_id=metadata.pool_id,
            df_balance_snapshots=df_balance_snapshots,
            snapshot_repository=snapshot_repository,
        )


def _import_blocks(
    block_heights: Iterable[int],
    block_client: BlockClient,
    block_repository: BlockRepository,
) -> None:

    for block_height in block_heights:
        if block_repository.get(block_height) is None:
            block: Block = block_client.get_block(block_height)
            block_repository.add(block)


def _import_staking_snapshots(
    account_key: str,
    pool_id: str,
    df_balance_snapshots: pl.DataFrame,
    snapshot_repository: SnapshotRepository,
) -> None:

    df_staking_snapshots: pl.DataFrame = create_staking_snapshots(
        account_key=account_key,
        pool_id=pool_id,
        df_balance_snapshots=df_balance_snapshots,
    )

    snapshot_repository.add_all(df_staking_snapshots)
