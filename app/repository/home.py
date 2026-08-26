from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import Mastery, StudyPlan, Wrongnote


class HomeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def count_due_review_concepts(self, user_id: int) -> int:
        # 홈 "다시 풀어볼 문제" - 에빙하우스 복습 예정(nextReviewAt <= now)인 개념 수
        # nextReviewAt이 아직 없는(null) 기존 row는 즉시 복습 대상으로 취급
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(func.count()).where(
                Mastery.userId == user_id,
                or_(Mastery.nextReviewAt <= now, Mastery.nextReviewAt.is_(None)),
            )
        )
        return result.scalar_one()

    async def count_due_wrongnotes(self, user_id: int) -> int:
        # 홈 복습 큐 - 오늘 복습 예정인 오답 수
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(func.count()).where(
                Wrongnote.userId == user_id,
                Wrongnote.reviewDueAt <= now,
            )
        )
        return result.scalar_one()

    async def has_study_plan(self, user_id: int) -> bool:
        # 홈 - 사용자가 STUDY_PLAN(주요 개념)을 하나라도 등록했는지 여부
        result = await self.db.execute(
            select(StudyPlan.id).where(StudyPlan.userId == user_id).limit(1)
        )
        return result.scalar_one_or_none() is not None
