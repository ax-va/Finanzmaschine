from typing import Self

from pydantic import model_validator
from sqlalchemy import BigInteger
from sqlmodel import Field

from fzm_staking.orm.near.key import Key


class SnapshotSearch(
    Key,
    table=True,
):
    """Represents the state and coverage of a staking snapshot search."""

    __tablename__ = "near_staking_snapshot_searches"

    from_block_height: int = Field(
        sa_type=BigInteger,
    )
    up_to_block_height: int | None = Field(
        default=None,
        sa_type=BigInteger,
    )

    started: bool = Field(default=False)
    stopped: bool = Field(default=False)
