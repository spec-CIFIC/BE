from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import Mastery, Wrongnote


class HomeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def count_weak_concepts(self, user_id: int, threshold: float = 0.4) -> int:
        # 홈 복습 큐 - 숙련도가 threshold 이하인 개념 수
        result = await self.db.execute(
            select(func.count()).where(
                Mastery.userId == user_id,
                Mastery.score <= threshold,
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
