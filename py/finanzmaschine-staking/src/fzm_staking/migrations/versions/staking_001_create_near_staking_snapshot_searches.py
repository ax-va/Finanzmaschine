from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "staking_001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "near_staking_snapshot_searches",
        sa.Column("account_key", sa.String(), nullable=False),
        sa.Column("pool_key", sa.String(), nullable=False),
        sa.Column("from_block_height", sa.BigInteger(), nullable=False),
        sa.Column("up_to_block_height", sa.BigInteger(), nullable=True),
        sa.Column("locked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.PrimaryKeyConstraint("account_key", "pool_key"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("near_staking_snapshot_searches")
