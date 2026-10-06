import logging
from datetime import datetime
from pathlib import Path

import polars as pl
import yaml

from fzm_staking.orm.near.balance import Balance
from fzm_staking.orm.near.key import Key

BLOCK_HEIGHT = "block_height"
STAKED_BALANCE_YOCTO_STR = "staked_balance_yocto_str"
UNSTAKED_BALANCE_YOCTO_STR = "unstaked_balance_yocto_str"
LOWER_BLOCK_HEIGHT = "lower_block_height"
UPPER_BLOCK_HEIGHT = "upper_block_height"
ACCOUNT_KEY = "account_key"
POOL_KEY = "pool_key"

logger = logging.getLogger(__name__)


class SnapshotStorage:
    """
    Stores staking snapshots that are collected during a staking snapshot search.

    Accumulates balances in memory between search iterations
    and persists staking snapshots to disk.
    """

    SCHEMA = {
        BLOCK_HEIGHT: pl.Int64,
        STAKED_BALANCE_YOCTO_STR: pl.String,
        UNSTAKED_BALANCE_YOCTO_STR: pl.String,
    }

    def __init__(
        self,
        key: Key,
        target_dir: str | Path | None = None,
    ) -> None:
        """
        Args:
            key: Staking key containing `account_key` and `pool_key`.
            target_dir:
                Directory where snapshots of processed intervals are saved.
                If omitted, a timestamped subdirectory is created in the current working directory.

        Raises:
            KeyError:
                From `self._validate_or_save_key`.
            ValueError:
                From `self._validate_or_save_key`.
        """
        self._key: Key = key
        self._df_balances = pl.DataFrame(schema=self.SCHEMA)

        if target_dir is not None:
            self._target_dir = Path(target_dir)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            self._target_dir = Path.cwd() / f"near_snapshots_{timestamp}"

        self._target_dir.mkdir(parents=True, exist_ok=True)

        self._validate_or_save_key()

    @property
    def key(self) -> Key:
        return self._key

    @property
    def df_balances(self) -> pl.DataFrame:
        return self._df_balances

    @property
    def target_dir(self) -> Path:
        return self._target_dir

    def add(
        self,
        balance: Balance,
    ) -> None:
        """
        Adds a balance snapshot to the in-memory storage.

        Args:
            balance: Balance snapshot to add.

        Raises:
            ValueError:
                If a balance snapshot with the same block height already exists.
        """
        df_duplicates: pl.DataFrame = self._df_balances.filter(
            (pl.col(BLOCK_HEIGHT) == balance.block_height)
        )

        if not df_duplicates.is_empty():
            raise ValueError(
                f"Snapshot already exists for {BLOCK_HEIGHT}={balance.block_height}"
            )

        df_row = pl.DataFrame(
            {
                BLOCK_HEIGHT: [balance.block_height],
                STAKED_BALANCE_YOCTO_STR: [balance.staked_balance_yocto_str],
                UNSTAKED_BALANCE_YOCTO_STR: [balance.unstaked_balance_yocto_str],
            },
            schema=self.SCHEMA,
        )

        self._df_balances: pl.DataFrame = (
            pl.concat([self._df_balances, df_row])
            .sort([BLOCK_HEIGHT])
        )

    def get(
        self,
        block_height: int,
    ) -> Balance | None:
        """
        Returns the balance snapshot at the given block height.

        Args:
            block_height: Block height of the balance snapshot to retrieve.

        Returns:
            The balance snapshot or `None`
            if no balance snapshot exists at the given block height.

        Raises:
            RuntimeError:
                If multiple balance snapshots exist at the given block height.
        """
        df_balance: pl.DataFrame = self._df_balances.filter(
            (pl.col(BLOCK_HEIGHT) == block_height)
        )

        if df_balance.is_empty():
            return None

        if df_balance.height > 1:
            raise RuntimeError(
                f"Multiple snapshots found for {BLOCK_HEIGHT}={block_height}"
            )

        row: dict = df_balance.row(0, named=True)

        return Balance(
            block_height=row[BLOCK_HEIGHT],
            staked_balance_yocto_str=row[STAKED_BALANCE_YOCTO_STR],
            unstaked_balance_yocto_str=row[UNSTAKED_BALANCE_YOCTO_STR],
        )

    def clear(self) -> None:
        """
        Clears balances accumulated in memory.

        Persisted snapshots are not affected.
        """
        self._df_balances = pl.DataFrame(schema=self.SCHEMA)

    def save(
        self,
        lower_block_height: int,
        upper_block_height: int,
    ) -> None:
        """
        Persists the current balance snapshots and their block interval.

        Args:
            lower_block_height: Lower block height, inclusive.
            upper_block_height: Upper block height, inclusive.

        Raises:
            ValueError: If `upper_block_height` is less than `lower_block_height`.
        """
        if upper_block_height < lower_block_height:
            raise ValueError(
                "`upper_block_height` must be greater than or equal to `lower_block_height`"
            )

        snapshots_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        balances_path = self._target_dir / f"balances_{snapshots_id}.csv"
        interval_path = self._target_dir / f"interval_{snapshots_id}.yaml"
        interval_data = {
            LOWER_BLOCK_HEIGHT: lower_block_height,
            UPPER_BLOCK_HEIGHT: upper_block_height,
        }

        logger.debug(
            f"Saving balances for block heights "
            f"{lower_block_height} to {upper_block_height}: {balances_path}"
        )

        self._df_balances.write_csv(balances_path)

        logger.debug(
            f"Saving interval for block heights "
            f"{lower_block_height} to {upper_block_height}: {interval_path}"
        )

        with interval_path.open("w", encoding="utf-8") as file:
            yaml.safe_dump(interval_data, file)

    def _validate_or_save_key(self) -> None:
        key_path = self._target_dir / "key.yaml"

        if key_path.exists():

            logger.debug(f"The key file already exists: {key_path}")

            with key_path.open("r", encoding="utf-8") as file:
                key: dict = yaml.safe_load(file) or {}

            logger.debug(f"Comparing the key in the key file with the current values")

            for key_name, expected in (
                (ACCOUNT_KEY, self._key.account_key),
                (POOL_KEY, self._key.pool_key),
            ):
                if key_name not in key:
                    raise KeyError(f"Missing `{key_name}` in {key_path}")

                actual = key[key_name]

                if actual != expected:
                    raise ValueError(
                        f"Expected `{key_name}` {expected}, "
                        f"but got {actual} in {key_path}"
                    )

        else:

            logger.debug(f"Saving key: {key_path}")

            with key_path.open("w", encoding="utf-8") as file:
                yaml.safe_dump(self._key.model_dump(), file)
