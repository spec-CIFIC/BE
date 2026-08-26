"""add_study_plan_table

Revision ID: 3815c50b15ea
Revises: faa3eb159683
Create Date: 2026-08-23 21:56:42.926207

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3815c50b15ea'
down_revision: Union[str, Sequence[str], None] = 'faa3eb159683'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'STUDY_PLAN',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('userId', sa.BigInteger(), nullable=False),
        sa.Column('conceptId', sa.BigInteger(), nullable=False),
        sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['conceptId'], ['CONCEPT.id'], ),
        sa.ForeignKeyConstraint(['userId'], ['USER.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('userId', 'conceptId', name='uq_study_plan_user_concept'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('STUDY_PLAN')
