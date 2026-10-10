from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "staking_001"
down_revision: Union[str, Sequence[str], None] = "staking_002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

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


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("near_staking_actions")
