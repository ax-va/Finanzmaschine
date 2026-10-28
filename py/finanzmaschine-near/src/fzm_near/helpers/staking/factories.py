import polars as pl

from fzm_near.helpers import constants as const
from fzm_near.helpers.staking.df_schemas import (
    BALANCE_SCHEMA,
    SNAPSHOT_SCHEMA,
    ACTION_SCHEMA,
    SEARCH_INTERVAL_SCHEMA,
    FINAL_STATE_SCHEMA,
)
from fzm_near.helpers.staking.enums import MethodNameEnum
from fzm_near.orm.staking.key import Key


class SnapshotFactory:
    """
    Creates staking snapshots from account and pool balance data.

    Combines staking keys with balance snapshots
    and produces dataframes conforming to the staking snapshot schema.
    """

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
    """
    Builds search intervals for historical staking pool balance changes.

    Constructs block-height intervals
    in which the total balance (staked + unstaked)
    is expected to be monotonically non-decreasing.

    Uses staking actions to determine interval boundaries
    and maintains a heuristic state indicating
    whether a search interval should remain logically open
    across consecutive block ranges.
    """

    @staticmethod
    def create_df_search_intervals_and_final_states(
        df_actions: pl.DataFrame,
        from_block_height: int,
        up_to_block_height: int,
        df_last_states: pl.DataFrame | None = None,
    ) -> dict[str, pl.DataFrame]:
        """
        Builds search intervals for staking pool total balance snapshots.

        Each interval represents a block-height range
        within which the account's total balance (staked + unstaked)
        is expected to be monotonically non-decreasing.
        The balance may increase due to staking rewards or deposits.

        Intervals are constructed independently for each staking pool #
        using successful contract actions grouped by block height.

        Interval construction rules:

            - `DEPOSIT_AND_STAKE`, `STAKE`, and `STAKE_ALL` activate
            reward tracking and open an interval if none is open.

            - `DEPOSIT` does not interrupt an open interval
            because it only increases the total balance.

            - `WITHDRAW` and `WITHDRAW_ALL` interrupt an open interval
            because they decrease the total balance.
            The previous interval ends at the preceding block,
            and a new interval starts at the withdrawal block.

            - `UNSTAKE_ALL` closes an open interval at its block height,
            unless a staking action occurs in the same block.

            - `UNSTAKE` does not affect interval boundaries.

            - `DEPOSIT` and withdrawal actions occurring
            while rewards are inactive produce single-block intervals.

        When multiple actions occur in the same block, they are evaluated together
        because only the final block snapshot is observable.
        Staking actions take precedence over `UNSTAKE_ALL`
        when determining whether reward tracking remains open.

        The initial reward-tracking state is taken from `df_last_states`.
        The `IS_OPEN` flag represents a heuristic estimate of
        whether the account may receive staking rewards.
        The flag is used to determine whether a search interval
        should remain open across block ranges.
        Pools without a previous state are considered inactive.
        Previously open pools remain searchable even if no new actions occur.

        Args:
            df_actions:
                Successful staking pool actions within the requested block-height range.
            from_block_height:
                Inclusive lower boundary of the search range.
            up_to_block_height:
                Inclusive upper boundary of the search range.
            df_last_states:
                Optional reward-tracking states from the previous range,
                containing one `IS_OPEN` value per pool.

        Returns:
            A dictionary containing keys:
                "search_intervals":
                    Block-height intervals for searching total balance snapshots.
                "final_states":
                    Reward-tracking states for each pool at the end of the requested range,
                    suitable for processing the next range.

        Raises:
            ValueError:
                - If an input dataframe has an invalid schema.
                - If the block-height range is invalid, an action falls outside the requested range.
                - If `df_last_states` contains multiple states for the same pool.
        """

        # Verify schema
        if not all(
            df_actions.schema.get(column) == dtype
            for column, dtype in ACTION_SCHEMA.items()
        ):
            raise ValueError(
                f"Expected `df_actions` schema to contain {ACTION_SCHEMA}, "
                f"got {df_actions.schema}"
            )

        if from_block_height > up_to_block_height:
            raise ValueError(
                "`from_block_height` must be less than "
                "or equal to `up_to_block_height`"
            )

        if df_last_states is None:
            df_last_states = pl.DataFrame(schema=FINAL_STATE_SCHEMA)
        else:
            # Verify schema
            if not all(
                df_last_states.schema.get(column) == dtype
                for column, dtype in FINAL_STATE_SCHEMA.items()
            ):
                raise ValueError(
                    f"Expected `df_last_states` schema to contain {FINAL_STATE_SCHEMA}, "
                    f"got {df_last_states.schema}"
                )

        is_open_by_pool: dict[str, bool] = {}

        # Check `df_last_states` and collect `is_open_by_pool`
        for (pool_key,), df_pool_last in df_last_states.group_by(
            const.POOL_KEY,
            maintain_order=True,
        ):
            if df_pool_last.height != 1:
                raise ValueError(
                    f"`df_last_states` must have at most "
                    f"one state for each pool: pool {pool_key}"
                )

            is_open_by_pool[pool_key] = df_pool_last.item(
                0, const.IS_OPEN
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

            # Determine whether it is currently possible
            # to open the first interval.
            lower_block_height: int | None = (
                from_block_height
                if is_open_by_pool.get(pool_key, False)
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

                if lower_block_height is not None:  # open search interval

                    has_withdraw = methods.is_in([
                        MethodNameEnum.WITHDRAW,
                        MethodNameEnum.WITHDRAW_ALL,
                    ]).any()

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
                        # Open a new interval
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

                    has_withdraw = methods.is_in([
                        MethodNameEnum.WITHDRAW,
                        MethodNameEnum.WITHDRAW_ALL,
                    ]).any()

                    has_deposit = (
                        methods == MethodNameEnum.DEPOSIT
                    ).any()

                    if has_withdraw or has_deposit:
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
                is_open=(lower_block_height is not None),
                final_states=final_states,
            )

        # Pools without new actions
        # may still require searching
        # if their previous state was open.
        for pool_key, is_open in is_open_by_pool.items():
            if pool_key in processed_pools:
                continue

            if is_open:
                SearchIntervalFactory._append_search_interval(
                    pool_key=pool_key,
                    lower_block_height=from_block_height,
                    upper_block_height=up_to_block_height,
                    intervals=intervals,
                )

            SearchIntervalFactory._append_final_state(
                pool_key=pool_key,
                is_open=is_open,
                final_states=final_states,
            )

        return {
            "search_intervals": pl.DataFrame(
                data=intervals,
                schema=SEARCH_INTERVAL_SCHEMA,
            ).sort([
                const.POOL_KEY,
                const.FROM_BLOCK_HEIGHT,
            ]),
            "final_states": pl.DataFrame(
                data=final_states,
                schema=FINAL_STATE_SCHEMA,
            ).sort([
                const.POOL_KEY,
            ])
        }

    @staticmethod
    def _append_search_interval(
        pool_key: str,
        lower_block_height: int,
        upper_block_height: int,
        intervals: list[dict],
    ) -> None:
        """
        Appends an inclusive block-height search interval.

        The interval includes both boundary blocks
        and must have a lower boundary not greater than its upper boundary.

        Raises:
            ValueError:
                If the upper boundary is below the lower boundary.
        """

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
        is_open: bool,
        final_states: list[dict],
    ) -> None:
        """
        Appends the final reward-tracking state for a staking pool.

        The state indicates whether the pool may continue
        receiving staking rewards in the next block-height range.
        """

        final_states.append(
            {
                const.POOL_KEY: pool_key,
                const.IS_OPEN: is_open,
            }
        )
