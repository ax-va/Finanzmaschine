from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "staking_002"
down_revision: Union[str, Sequence[str], None] = "staking_001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table("near_staking_snapshots",
        sa.Column("account_key", sa.String(), nullable=False),
        sa.Column("pool_key", sa.String(), nullable=False),
        sa.Column("block_height", sa.BigInteger(), nullable=False),
        sa.Column("staked_yocto_str", sa.String(), nullable=False),
        sa.Column("unstaked_yocto_str", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint( "account_key", "pool_key", "block_height")
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("near_staking_snapshots")
