from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "staking_near_001"
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

    op.create_table(
        "near_staking_actions",
        sa.Column("receipt_key", sa.String(), nullable=False),
        sa.Column("action_index", sa.Integer(), nullable=False),
        sa.Column("transaction_key", sa.String(), nullable=False),
        sa.Column("account_key", sa.String(), nullable=False),
        sa.Column("pool_key", sa.String(), nullable=False),
        sa.Column("tx_block_height", sa.BigInteger(), nullable=False),
        sa.Column("receipt_block_height", sa.BigInteger(), nullable=False),
        sa.Column("action_type", sa.String(), nullable=False),
        sa.Column("operation_yocto_str", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("receipt_key", "action_index"),
    )

    for column in (
            "transaction_key",
            "account_key",
            "pool_key",
            "tx_block_height",
            "receipt_block_height",
    ):
        op.create_index(
            f"ix_near_staking_actions_{column}",
            "near_staking_actions",
            [column],
        )

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
    op.drop_table("near_staking_actions")
    op.drop_table("near_staking_snapshot_searches")