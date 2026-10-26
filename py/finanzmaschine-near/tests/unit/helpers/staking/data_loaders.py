from pathlib import Path

import polars as pl

from fzm_near.helpers.staking.df_schemas import (
    ACTION_SCHEMA,
    FINAL_STATE_SCHEMA,
    SEARCH_INTERVAL_SCHEMA,
)


def load_actions(file_path: Path) -> pl.DataFrame:
    df = pl.read_csv(file_path)

    return df.with_columns(
        pl.lit(None).cast(dtype).alias(column)
        for column, dtype in ACTION_SCHEMA.items()
        if column not in df.columns
    ).cast(ACTION_SCHEMA)


def load_expected_final_states(file_path: Path) -> pl.DataFrame:
    return pl.read_csv(file_path, schema_overrides=FINAL_STATE_SCHEMA)


def load_expected_search_intervals(file_path: Path) -> pl.DataFrame:
    return pl.read_csv(file_path, schema_overrides=SEARCH_INTERVAL_SCHEMA)
