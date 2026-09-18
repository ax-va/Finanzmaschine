from datetime import datetime
from pathlib import Path

import polars as pl

from finanzmaschine_staking.orm.near.balance_snapshot import BalanceSnapshot

BLOCK_HEIGHT = "block_height"
STAKED_BALANCE_YOCTO_STR = "staked_balance_yocto_str"
UNSTAKED_BALANCE_YOCTO_STR = "unstaked_balance_yocto_str"

SCHEMA = {
    BLOCK_HEIGHT: pl.Int64,
    STAKED_BALANCE_YOCTO_STR: pl.String,
    UNSTAKED_BALANCE_YOCTO_STR: pl.String,
}

near_balance_snapshots = pl.DataFrame(schema=SCHEMA)


def add_snapshot(snapshot: BalanceSnapshot) -> None:
    global near_balance_snapshots

    df_duplicate = near_balance_snapshots.filter(
        (pl.col(BLOCK_HEIGHT) == snapshot.block_height)
    )

    if not df_duplicate.is_empty():
        raise ValueError(
            f"Snapshot already exists for {BLOCK_HEIGHT}={snapshot.block_height}"
        )

    df_row = pl.DataFrame(
        {
            BLOCK_HEIGHT: [snapshot.block_height],
            STAKED_BALANCE_YOCTO_STR: [snapshot.staked_balance_yocto_str],
            UNSTAKED_BALANCE_YOCTO_STR: [snapshot.unstaked_balance_yocto_str],
        },
        schema=SCHEMA,
    )

    near_balance_snapshots = (
        pl.concat([near_balance_snapshots, df_row])
        .sort([BLOCK_HEIGHT])
    )


def get_snapshot(block_height: int) -> BalanceSnapshot | None:
    df_snapshot = near_balance_snapshots.filter(
        (pl.col(BLOCK_HEIGHT) == block_height)
    )

    if df_snapshot.is_empty():
        return None

    if df_snapshot.height > 1:
        raise RuntimeError(
            f"Multiple snapshots found for {BLOCK_HEIGHT}={block_height}"
        )

    row = df_snapshot.row(0, named=True)

    return BalanceSnapshot(
        block_height=row[BLOCK_HEIGHT],
        staked_balance_yocto_str=row[STAKED_BALANCE_YOCTO_STR],
        unstaked_balance_yocto_str=row[UNSTAKED_BALANCE_YOCTO_STR],
    )


def save_snapshots(target_dir: str | Path | None = None) -> None:
    target_dir = Path(target_dir) if target_dir is not None else Path.cwd()
    target_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

    file_stem = (
        target_dir / f"near_balance_snapshots_{timestamp}"
    )

    near_balance_snapshots.write_csv(
        file_stem.with_suffix(".csv")
    )
    near_balance_snapshots.write_parquet(
        file_stem.with_suffix(".parquet")
    )


def clear_snapshots() -> None:
    global near_balance_snapshots

    near_balance_snapshots = pl.DataFrame(schema=SCHEMA)
