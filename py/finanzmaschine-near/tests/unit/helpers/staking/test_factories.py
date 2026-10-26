import polars as pl
import pytest
from polars.testing import assert_frame_equal

from fzm_near.helpers.staking.factories import SearchIntervalFactory


@pytest.mark.parametrize(
    "actions, expected_search_intervals, expected_final_states, from_block_height, up_to_block_height",
    [
        (
            "simple_actions",
            "simple_expected_search_intervals",
            "simple_expected_final_states",
            100,
            500,
        ),
    ],
)
def test_create_df_search_intervals_and_final_states(
    request: pytest.FixtureRequest,
    actions: str,
    expected_search_intervals: str,
    expected_final_states: str,
    from_block_height: int,
    up_to_block_height: int,
):
    df_actions: pl.DataFrame = request.getfixturevalue(actions)
    df_expected_intervals: pl.DataFrame = request.getfixturevalue(expected_search_intervals)
    df_expected_states: pl.DataFrame = request.getfixturevalue(expected_final_states)

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
