"""refactor_question_type_add_is_ai_generated

Revision ID: faa3eb159683
Revises: ccc6193aa22a
Create Date: 2026-08-23 19:35:23.264855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'faa3eb159683'
down_revision: Union[str, Sequence[str], None] = 'ccc6193aa22a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. isAiGenerated 컬럼 추가 (기존 행은 일단 True로)
    op.add_column('QUESTIONS', sa.Column('isAiGenerated', sa.Boolean(), nullable=False, server_default='true'))

    # 2. 기출문제(PAST_EXAM)는 isAiGenerated=False로 설정 (questionType 변경 전에 처리)
    op.execute("UPDATE \"QUESTIONS\" SET \"isAiGenerated\" = false WHERE \"questionType\" = 'PAST_EXAM'")

    # 3. questionType 값 정리: GENERATED → CALCULATION, PAST_EXAM → CALCULATION
    op.execute("UPDATE \"QUESTIONS\" SET \"questionType\" = 'CALCULATION' WHERE \"questionType\" IN ('GENERATED', 'PAST_EXAM')")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("UPDATE \"QUESTIONS\" SET \"questionType\" = 'GENERATED' WHERE \"isAiGenerated\" = true AND \"questionType\" = 'CALCULATION'")
    op.execute("UPDATE \"QUESTIONS\" SET \"questionType\" = 'PAST_EXAM' WHERE \"isAiGenerated\" = false")
    op.drop_column('QUESTIONS', 'isAiGenerated')
