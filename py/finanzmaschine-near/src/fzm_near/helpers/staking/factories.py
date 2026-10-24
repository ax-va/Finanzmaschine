import polars as pl

from fzm_near.helpers import constants as const
from fzm_near.helpers.staking.df_schemas import (
    BALANCE_SCHEMA,
    SNAPSHOT_SCHEMA,
    FINAL_STATE_SCHEMA,
    SEARCH_INTERVAL_SCHEMA,
)
from fzm_near.helpers.staking.enums import MethodNameEnum
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


class SearchIntervalFactory:

    @staticmethod
    def create_df_search_intervals(
        df_actions: pl.DataFrame,
        from_block_height: int,
        up_to_block_height: int,
        df_last_states: pl.DataFrame | None = None,
    ) -> dict[str, pl.DataFrame]:
        """Builds block-height intervals for searching staking pool balance changes."""

        if from_block_height > up_to_block_height:
            raise ValueError(
                "`from_block_height` must be less than "
                "or equal to `up_to_block_height`"
            )

        if df_last_states is None:
            df_last_states = pl.DataFrame(
                schema=FINAL_STATE_SCHEMA,
            )

        is_active_by_pool: dict[str, bool] = {}

        # Check `df_last_states` and collect `is_active_by_pool`
        for (pool_key,), df_pool_last in df_last_states.group_by(
            const.POOL_KEY,
            maintain_order=True,
        ):
            if df_pool_last.height != 1:
                raise ValueError(
                    f"`df_last_states` must have at most "
                    f"one state for each pool: pool {pool_key}"
                )

            is_active_by_pool[pool_key] = df_pool_last.item(
                0, const.IS_ACTIVE
            )

        intervals: list[dict] = []
        final_states: list[dict] = []
        processed_pools: set[str] = set()

        # Iterate through pools
        for (pool_key,), df_pool in df_actions.group_by(
            const.POOL_KEY,
            maintain_order=True,
        ):
            processed_pools.add(pool_key)

            df_pool = df_pool.sort([
                const.EXEC_OUTCOME_BLOCK_HEIGHT,
            ])

            min_height = df_pool.item(
                0, const.EXEC_OUTCOME_BLOCK_HEIGHT
            )
            max_height = df_pool.item(
                -1, const.EXEC_OUTCOME_BLOCK_HEIGHT
            )

            if min_height < from_block_height:
                raise ValueError(
                    f"Action block height {min_height} is below "
                    f"`from_block_height`: pool {pool_key}"
                )

            if max_height > up_to_block_height:
                raise ValueError(
                    f"Action block height {max_height} exceeds "
                    f"`up_to_block_height`: pool {pool_key}"
                )

            # Determine
            # whether it is currently possible
            # to open the first interval.
            lower_block_height: int | None = (
                from_block_height
                if is_active_by_pool.get(pool_key, False)
                else None
            )

            # Iterate through blocks
            for (block_height,), df_block in df_pool.group_by(
                const.EXEC_OUTCOME_BLOCK_HEIGHT,
                maintain_order=True,
            ):
                methods: pl.Series = df_block[const.METHOD_NAME]

                has_stake = methods.is_in([
                    MethodNameEnum.STAKE,
                    MethodNameEnum.STAKE_ALL,
                    MethodNameEnum.DEPOSIT_AND_STAKE,
                ]).any()

                has_withdraw = methods.is_in([
                    MethodNameEnum.WITHDRAW,
                    MethodNameEnum.WITHDRAW_ALL,
                ]).any()

                if lower_block_height is not None:  # active rewards

                    has_unstake_all = (
                        methods == MethodNameEnum.UNSTAKE_ALL
                    ).any()

                    # At first, check `WITHDRAW...`
                    if has_withdraw:
                        if lower_block_height < block_height:
                            SearchIntervalFactory._append_search_interval(
                                pool_key=pool_key,
                                lower_block_height=lower_block_height,
                                upper_block_height=block_height - 1,
                                intervals=intervals,
                            )
                        lower_block_height = block_height

                    # Then, check `UNSTAKE_ALL` without `...STAKE...`
                    if has_unstake_all and not has_stake:
                        # noinspection PyTypeChecker
                        SearchIntervalFactory._append_search_interval(
                            pool_key=pool_key,
                            lower_block_height=lower_block_height,
                            upper_block_height=block_height,
                            intervals=intervals,
                        )
                        lower_block_height = None

                else:  # inactive rewards

                    if has_stake:
                        lower_block_height = block_height
                        continue

                    has_deposit = (
                        methods == MethodNameEnum.DEPOSIT
                    ).any()

                    if has_deposit or has_withdraw:
                        SearchIntervalFactory._append_search_interval(
                            pool_key=pool_key,
                            lower_block_height=block_height,
                            upper_block_height=block_height,
                            intervals=intervals,
                        )

            if lower_block_height is not None:
                # Close the final interval
                # and add it to the intervals.
                SearchIntervalFactory._append_search_interval(
                    pool_key=pool_key,
                    lower_block_height=lower_block_height,
                    upper_block_height=up_to_block_height,
                    intervals=intervals,
                )

            SearchIntervalFactory._append_final_state(
                pool_key=pool_key,
                is_active=(lower_block_height is not None),
                final_states=final_states,
            )

        # Pools without new actions
        # may still require searching
        # if their previous state was active.
        for pool_key, is_active in is_active_by_pool.items():
            if pool_key in processed_pools:
                continue

            if is_active:
                SearchIntervalFactory._append_search_interval(
                    pool_key=pool_key,
                    lower_block_height=from_block_height,
                    upper_block_height=up_to_block_height,
                    intervals=intervals,
                )

            SearchIntervalFactory._append_final_state(
                pool_key=pool_key,
                is_active=is_active,
                final_states=final_states,
            )

        return {
            "search_intervals": pl.DataFrame(
                data=intervals,
                schema=SEARCH_INTERVAL_SCHEMA,
            ),
            "final_states": pl.DataFrame(
                data=final_states,
                schema=FINAL_STATE_SCHEMA,
            )
        }

    @staticmethod
    def _append_search_interval(
        pool_key: str,
        lower_block_height: int,
        upper_block_height: int,
        intervals: list[dict],
    ) -> None:
        """Append a non-empty search interval."""

        if upper_block_height < lower_block_height:
            raise ValueError(
                "`lower_block_height` must be less than or equal to `upper_block_height`"
            )

        intervals.append({
            const.POOL_KEY: pool_key,
            const.FROM_BLOCK_HEIGHT: lower_block_height,
            const.UP_TO_BLOCK_HEIGHT: upper_block_height,
        })

    @staticmethod
    def _append_final_state(
        pool_key: str,
        is_active: bool,
        final_states: list[dict],
    ) -> None:

        final_states.append(
            {
                const.POOL_KEY: pool_key,
                const.IS_ACTIVE: is_active,
            }
        )
