"""add subjectId to anon_session

Revision ID: a1b2c3d4e5f6
Revises: 7dc2f2c87fa4
Create Date: 2026-08-20 16:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '7dc2f2c87fa4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'ANON_SESSION',
        sa.Column('subjectId', sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        'fk_anon_session_subject',
        'ANON_SESSION',
        'SUBJECT',
        ['subjectId'],
        ['id'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_anon_session_subject', 'ANON_SESSION', type_='foreignkey')
    op.drop_column('ANON_SESSION', 'subjectId')
