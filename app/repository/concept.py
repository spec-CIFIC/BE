from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import Concept


class ConceptRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_ids(self, ids: list[int]) -> list[Concept]:
        # GET /intro/report predictedWeak 구성 — 자가진단 개념 ID로 개념 정보 조회
        if not ids:
            return []
        result = await self.db.execute(
            select(Concept).where(Concept.id.in_(ids))
        )
        return list(result.scalars().all())

    async def find_all(self) -> list[Concept]:
        # GET /intro/questions 폴백 — 자가진단 없을 때 전체 개념 대상 문제 조회
        result = await self.db.execute(select(Concept))
        return list(result.scalars().all())
