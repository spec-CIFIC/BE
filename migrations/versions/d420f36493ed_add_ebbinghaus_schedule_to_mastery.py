"""add ebbinghaus schedule to mastery

Revision ID: d420f36493ed
Revises: 3815c50b15ea
Create Date: 2026-08-25 16:34:33.377567

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd420f36493ed'
down_revision: Union[str, Sequence[str], None] = '3815c50b15ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 기존 MASTERY row 보호를 위해 server_default='0' 부여 (신규 insert는 ORM 기본값 사용)
    op.add_column(
        'MASTERY',
        sa.Column('reviewStage', sa.Integer(), nullable=False, server_default='0'),
    )
    op.add_column(
        'MASTERY',
        sa.Column('nextReviewAt', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('MASTERY', 'nextReviewAt')
    op.drop_column('MASTERY', 'reviewStage')
