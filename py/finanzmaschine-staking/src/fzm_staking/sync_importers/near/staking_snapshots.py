import logging
from pathlib import Path
from typing import Iterable

import polars as pl

from fzm_staking.dfs.near.staking_snapshots import (
    create_df_staking_snapshots,
    load_key,
    load_df_balances,
)
from fzm_crypto.orm.near.block import Block
from fzm_crypto.sync_clients.near.block_client import BlockClient
from fzm_staking.orm.near.snapshot import Snapshot
from fzm_staking.orm.near.key import Key
from fzm_staking.storage.near.snapshot_storage import BLOCK_HEIGHT
from fzm_staking.sync_repositories.near.block_repository import BlockRepository
from fzm_staking.sync_repositories.near.snapshot_repository import SnapshotRepository

logger = logging.getLogger(__name__)


def import_staking_snapshots(
    source_dir: str | Path,
    block_client: BlockClient,
    block_repository: BlockRepository,
    snapshot_repository: SnapshotRepository,
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
        block_client:
            NEAR block client used to fetch blocks missing from the database.
        block_repository:
            Repository used to retrieve and persist blocks.
        snapshot_repository:
            Repository used to persists staking snapshots.
    """

    logger.info("Starting staking snapshots import to the database")

    source_dir = Path(source_dir)

    logger.info(f"Source directory: {source_dir}")

    key: Key = load_key(source_dir / "key.yaml")

    logger.info(f"Account key: {key.account_key}")
    logger.info(f"Pool key: {key.pool_key}")

    csv_paths: list[Path] = sorted(source_dir.glob("*.csv"))
    num_csv_paths: int = len(csv_paths)

    logger.info(f"Found {num_csv_paths} CSV files")

    for index, csv_path in enumerate(csv_paths, start=1):

        logger.info(
            f"Importing balance snapshots {index}/{num_csv_paths}: {csv_path.name}"
        )

        df_balances: pl.DataFrame = load_df_balances(csv_path)

        logger.debug(f"Loaded {df_balances.height} balance snapshots")

        imported_blocks_count: int = _import_blocks(
            block_heights=df_balances[BLOCK_HEIGHT],
            block_client=block_client,
            block_repository=block_repository,
        )

        logger.debug(f"Imported {imported_blocks_count} blocks")

        imported_snapshots_count: int = _import_staking_snapshots(
            key=key,
            df_balances=df_balances,
            snapshot_repository=snapshot_repository,
        )

        logger.debug(f"Imported {imported_snapshots_count} staking snapshots")

    logger.info(f"Processed {num_csv_paths} staking snapshot files")


def _import_blocks(
    block_heights: Iterable[int],
    block_client: BlockClient,
    block_repository: BlockRepository,
) -> int:
    """
    Imports blocks that are missing from the database.

    Existing blocks are skipped.
    Missing blocks are fetched using `block_client`
    and inserted through `block_repository`.

    Args:
        block_heights: Block height to ensure exist in the database.
        block_client: NERA block client used to fetch missing blocks.
        block_repository: Repository used to retrieve and persist blocks.

    Returns:
        The number of blocks successfully imported.
    """

    logger.debug("Importing missing blocks to the database")

    imported_count: int = 0

    for block_height in block_heights:

        if block_repository.get(block_height) is None:
            block: Block = block_client.get_block(block_height)

            if block_repository.safe_add(block):
                imported_count += 1
                logger.debug(f"Imported block {block_height}")
            else:
                logger.warning(
                    f"Block {block.block_height} was not inserted "
                    f"due to an integrity conflict"
                )

    return imported_count


def _import_staking_snapshots(
    key: Key,
    df_balances: pl.DataFrame,
    snapshot_repository: SnapshotRepository,
) -> int:
    """
    Imports staking snapshots into the database.

    Snapshots that cause an integrity conflict are not imported.

    Args:
        key: Snapshot key containing the account and pool keys.
        df_balances: Dataframe containing balance snapshots to import.
        snapshot_repository: Repository used to persist staking snapshots.

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
        snapshot: Snapshot = Snapshot.model_validate(row)

        if snapshot_repository.safe_add(snapshot):
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
