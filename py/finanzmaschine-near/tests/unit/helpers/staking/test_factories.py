from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from fzm_near.helpers.staking.factories import SearchIntervalFactory
from tests.unit.helpers.staking.data_loaders import (
    load_actions,
    load_expected_final_states,
    load_expected_search_intervals,
)


@pytest.mark.parametrize(
    "actions_file, "
    "expected_search_intervals_file, "
    "expected_final_states_file, "
    "block_ranges",
    [
        (
            "helpers/staking/single_pools/actions.csv",
            "helpers/staking/single_pools/expected_search_intervals.csv",
            "helpers/staking/single_pools/expected_final_states.csv",
            [(100, 999)],
        ),
        (
            "helpers/staking/multiple_pools/actions.csv",
            "helpers/staking/multiple_pools/expected_search_intervals.csv",
            "helpers/staking/multiple_pools/expected_final_states.csv",
            [(100, 999)],
        ),
        (
            "helpers/staking/complex_blocks/actions.csv",
            "helpers/staking/complex_blocks/expected_search_intervals.csv",
            "helpers/staking/complex_blocks/expected_final_states.csv",
            [(100, 999)],
        ),
        (
            "helpers/staking/with_last_states/actions.csv",
            "helpers/staking/with_last_states/expected_search_intervals.csv",
            "helpers/staking/with_last_states/expected_final_states.csv",
            [(100, 299), (300, 499), (500, 599), (600, 999)],
        )
    ],
)
def test_create_df_search_intervals_and_final_states(
    data_dir: Path,
    actions_file: str,
    expected_search_intervals_file: str,
    expected_final_states_file: str,
    block_ranges: list[tuple[int, int]],
):
    df_actions: pl.DataFrame = load_actions(
        data_dir / actions_file,
    )
    df_expected_intervals: pl.DataFrame = load_expected_search_intervals(
        data_dir / expected_search_intervals_file,
    )
    df_expected_states: pl.DataFrame = load_expected_final_states(
        data_dir / expected_final_states_file,
    )

    states_offset: int = 0
    df_last_states: pl.DataFrame | None = None
    for from_block_height, up_to_block_height in block_ranges:

        df_actions_slice: pl.DataFrame = df_actions.filter(
            pl.col("exec_outcome_block_height").is_between(
                from_block_height,
                up_to_block_height,
            )
        )

        # Compute the number of unique pools
        # that can be variable.
        pool_keys: pl.Series = df_actions_slice["pool_key"]
        if df_last_states is not None:
            pool_keys = pool_keys.append(df_last_states["pool_key"])
        num_pools = pool_keys.n_unique()

        result: dict[str, pl.DataFrame] = SearchIntervalFactory.create_df_search_intervals_and_final_states(
            df_actions=df_actions_slice,
            from_block_height=from_block_height,
            up_to_block_height=up_to_block_height,
            df_last_states=df_last_states,
        )

        df_expected_intervals_slice: pl.DataFrame = df_expected_intervals.filter(
            (pl.col("from_block_height") >= from_block_height)
            & (pl.col("up_to_block_height") <= up_to_block_height),
        )

        assert_frame_equal(
            result["search_intervals"],
            df_expected_intervals_slice,
        )

        assert_frame_equal(
            result["final_states"],
            df_expected_states.slice(states_offset, num_pools),
        )

        states_offset += num_pools
        df_last_states = result["final_states"]

    # Each action must be at least in one block range
    assert all(
        any(
            from_block_height <= block_height <= up_to_block_height
            for from_block_height, up_to_block_height in block_ranges
        )
        for block_height in df_actions["exec_outcome_block_height"]
    )

    assert states_offset == df_expected_states.height
