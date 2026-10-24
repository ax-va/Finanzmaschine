import polars as pl

from fzm_near.helpers import constants as const
from fzm_near.helpers.staking.df_schemas import (
    BALANCE_SCHEMA,
    SNAPSHOT_SCHEMA,
)
from fzm_near.orm.staking.key import Key


class SnapshotFactory:

    @staticmethod
    def create_df_snapshots(
        key: Key,
        df_balances: pl.DataFrame,
    ) -> pl.DataFrame:
        """
        Creates staking snapshots dataframe from staking key and balance snapshots.

        Adds the account and pool keys to each balance snapshot.

        If `df_balances` is empty, returns
        an empty dataframe with the staking snapshot schema.

        Args:
            key: Staking key containing account and pool keys.
            df_balances: Dataframe containing balance snapshots.

        Returns:
            A dataframe containing staking snapshots.

        Raises:
            ValueError:
                If `df_balances` does not contain the columns
                and data types defined by `BALANCE_SCHEMA`.
        """

        # Validate schema
        if not all(
            df_balances.schema.get(column) == dtype
            for column, dtype in BALANCE_SCHEMA.items()
        ):
            raise ValueError(
                f"Expected schema to contain {BALANCE_SCHEMA}, "
                f"got {df_balances.schema}"
            )

        if df_balances.is_empty():
            return pl.DataFrame(schema=SNAPSHOT_SCHEMA)

        return pl.DataFrame(
            data={
                const.ACCOUNT_KEY: key.account_key,
                const.POOL_KEY: key.pool_key,
                const.BLOCK_HEIGHT: df_balances[const.BLOCK_HEIGHT],
                const.STAKED_YOCTO_STR: df_balances[const.STAKED_YOCTO_STR],
                const.UNSTAKED_YOCTO_STR: df_balances[const.UNSTAKED_YOCTO_STR],
            },
            schema=SNAPSHOT_SCHEMA,
        )
