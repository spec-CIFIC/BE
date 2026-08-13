from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import Subject


class SubjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_all(self) -> list[Subject]:
        # GET /subjects 과목 목록 조회 — 과목 수가 적고 변경 빈도 낮음
        # 트래픽 증가 시 캐싱 도입 여지 있음
        result = await self.db.execute(select(Subject))
        return list(result.scalars().all())
