from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import Questions, Subject


class SubjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_all_with_question_count(self) -> list[tuple]:
        # GET /subjects — 과목 목록 + APPROVED 문제 수 집계
        stmt = (
            select(
                Subject.id,
                Subject.subjectName,
                func.count(Questions.id).label("questionCount"),
            )
            .outerjoin(
                Questions,
                (Questions.subjectId == Subject.id) & (Questions.status == "APPROVED"),
            )
            .group_by(Subject.id, Subject.subjectName)
            .order_by(Subject.id)
        )
        result = await self.db.execute(stmt)
        return list(result.all())

    async def find_by_ids(self, ids: list[int]) -> list[Subject]:
        # GET /intro/report predictedWeak 구성 — 자가진단 과목 ID로 과목 정보 조회
        if not ids:
            return []
        result = await self.db.execute(
            select(Subject).where(Subject.id.in_(ids))
        )
        return list(result.scalars().all())
