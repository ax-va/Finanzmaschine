import logging
from pathlib import Path
from typing import Iterable

import polars as pl

from finanzmaschine_staking.dataframes.near.staking_snapshots import (
    create_staking_snapshots,
    load_snapshots_metadata,
    load_balance_snapshots,
)
from finanzmaschine_staking.orm.near.block import Block
from finanzmaschine_staking.orm.near.snapshot_metadata import SnapshotMetadata
from finanzmaschine_staking.orm.near.staking_snapshot import StakingSnapshot
from finanzmaschine_staking.repositories.near.block_repository import BlockRepository
from finanzmaschine_staking.repositories.near.snapshot_repository import SnapshotRepository
from finanzmaschine_staking.storage.near.snapshot_storage import BLOCK_HEIGHT
from finanzmaschine_staking.sync_clients.near.block_client import BlockClient

logger = logging.getLogger(__name__)


def import_staking_snapshots(
    source_dir: str | Path,
    block_client: BlockClient,
    block_repository: BlockRepository,
    snapshot_repository: SnapshotRepository,
) -> None:
    source_dir = Path(source_dir)

    logger.info(
        f"Starting staking snapshots import from {source_dir!r} "
        f"to the {StakingSnapshot.__tablename__} table"
    )

    metadata: SnapshotMetadata = load_snapshots_metadata(source_dir / "near_metadata.yaml")

    parquet_paths: list[Path] = sorted(source_dir.glob("*.parquet"))

    logger.info(f"Found {len(parquet_paths)} snapshot files for pool {metadata.pool_id}")

    for index, parquet_path in enumerate(parquet_paths, start=1):

        logger.info(
            f"Importing snapshot file {index}/{len(parquet_paths)}: {parquet_path.name}"
        )

        df_balance_snapshots: pl.DataFrame = load_balance_snapshots(parquet_path)

        logger.debug(
            f"Loaded {df_balance_snapshots.height} balance snapshots from {parquet_path.name!r}"
        )

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

    logger.info(f"Completed staking snapshots import")


def _import_blocks(
    block_heights: Iterable[int],
    block_client: BlockClient,
    block_repository: BlockRepository,
) -> None:

    imported_count: int = 0

    for block_height in block_heights:
        if block_repository.get(block_height) is None:

            logger.debug(
                f"Importing block {block_height} to the {Block.__tablename__} table"
            )

            block: Block = block_client.get_block(block_height)
            block_repository.add(block)
            imported_count += 1

    logger.debug(f"Imported {imported_count} missing blocks")


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

    logger.debug(f"Imported {df_staking_snapshots.height} staking snapshots")
