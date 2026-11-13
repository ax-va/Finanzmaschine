from sqlalchemy import BigInteger
from sqlmodel import Field

from fzm_near.orm.staking.key import Key


class SnapshotSearch(Key, table=True):
    """Represents the state and coverage of a staking snapshot search."""

    __tablename__ = "near_staking_snapshot_searches"

    # Inclusive block height, up to which
    # the staking snapshot search is processed.
    up_to_block_height: int | None = Field(
        default=None,
        sa_type=BigInteger,
    )

    # Whether reward tracking remains active across block ranges
    is_reward_tracking_active: bool = Field(default=False)

    # Whether the search is locked for other processes
    is_locked: bool = Field(default=False)
