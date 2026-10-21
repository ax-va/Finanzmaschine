from pathlib import Path

import polars as pl
import yaml

from fzm_near.helpers.staking.df_schemas import BALANCE_SCHEMA
from fzm_near.orm.staking.key import Key


def load_df_balances(file_path: str | Path) -> pl.DataFrame:
    """
    Loads balance snapshots from a CSV file.

    Args:
        file_path: Path to CSV file containing balance snapshots.

    Returns:
        A dataframe containing the loaded balance snapshots.
    """
    return pl.read_csv(
        file_path,
        schema_overrides=BALANCE_SCHEMA,
    )


def load_key(file_path: str | Path) -> Key:
    """
    Loads staking key from a YAML file.

    Args:
        file_path: Path to the YAML file containing account and pool keys.

    Returns:
        A staking key.
    """
    with Path(file_path).open("r", encoding="utf-8") as file:
        return Key.model_validate(yaml.safe_load(file))
