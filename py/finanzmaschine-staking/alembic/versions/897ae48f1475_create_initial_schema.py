"""create initial schema

Revision ID: 897ae48f1475
Revises: 
Create Date: 2026-09-22 18:40:37.374480

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '897ae48f1475'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('near_blocks',
        sa.Column('block_height', sa.BigInteger(), nullable=False),
        sa.Column('timestamp_nanoseconds', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('block_height')
    )

    op.create_table('near_staking_snapshots',
        sa.Column('account_key', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('pool_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('block_height', sa.BigInteger(), nullable=False),
        sa.Column('staked_balance_yocto_str', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('unstaked_balance_yocto_str', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(['block_height'], ['near_blocks.block_height'], ),
        sa.PrimaryKeyConstraint( 'account_key', 'pool_id', 'block_height')
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
