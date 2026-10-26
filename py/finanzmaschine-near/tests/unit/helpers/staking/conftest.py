import polars as pl
import pytest

from fzm_near.helpers.staking.df_schemas import (
    ACTION_SCHEMA,
    FINAL_STATE_SCHEMA,
    SEARCH_INTERVAL_SCHEMA,
)


@pytest.fixture
def simple_actions(data_dir) -> pl.DataFrame:
    df = pl.read_csv(
        data_dir / "helpers/staking/simple/actions.csv",
    )

    return df.with_columns(
        pl.lit(None).cast(dtype).alias(column)
        for column, dtype in ACTION_SCHEMA.items()
        if column not in df.columns
    ).cast(ACTION_SCHEMA)


@pytest.fixture
def simple_expected_final_states(data_dir) -> pl.DataFrame:
    return pl.read_csv(
        data_dir / "helpers/staking/simple/expected_final_states.csv",
        schema_overrides=FINAL_STATE_SCHEMA,
    )


@pytest.fixture
def simple_expected_search_intervals(data_dir) -> pl.DataFrame:
    return pl.read_csv(
        data_dir / "helpers/staking/simple/expected_search_intervals.csv",
        schema_overrides=SEARCH_INTERVAL_SCHEMA,
    )
