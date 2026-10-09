from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "crypto_near_001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table("near_blocks",
        sa.Column("block_height", sa.BigInteger(), nullable=False),
        sa.Column("timestamp_nanoseconds", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("block_height")
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("near_blocks")
