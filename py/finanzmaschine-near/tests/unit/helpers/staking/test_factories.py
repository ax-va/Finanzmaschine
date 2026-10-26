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
    "actions_file, expected_search_intervals_file, expected_final_states_file, from_block_height, up_to_block_height",
    [
        (
            "helpers/staking/simple/actions.csv",
            "helpers/staking/simple/expected_search_intervals.csv",
            "helpers/staking/simple/expected_final_states.csv",
            100,
            500,
        ),
        (
            "helpers/staking/multiple_pools/actions.csv",
            "helpers/staking/multiple_pools/expected_search_intervals.csv",
            "helpers/staking/multiple_pools/expected_final_states.csv",
            100,
            500,
        )
    ],
)
def test_create_df_search_intervals_and_final_states(
    data_dir: Path,
    actions_file: str,
    expected_search_intervals_file: str,
    expected_final_states_file: str,
    from_block_height: int,
    up_to_block_height: int,
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

    result = SearchIntervalFactory.create_df_search_intervals_and_final_states(
        df_actions=df_actions,
        from_block_height=from_block_height,
        up_to_block_height=up_to_block_height,
    )

    assert_frame_equal(
        result["search_intervals"],
        df_expected_intervals,
    )

    assert_frame_equal(
        result["final_states"],
        df_expected_states,
    )
