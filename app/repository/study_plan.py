from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import StudyPlan


class StudyPlanRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_user(self, user_id: int) -> list[StudyPlan]:
        # GET /study-plan — 사용자가 등록한 주요 개념 목록 (concept은 lazy=selectin으로 로드)
        result = await self.db.execute(
            select(StudyPlan)
            .where(StudyPlan.userId == user_id)
            .order_by(StudyPlan.createdAt.asc())
        )
        return list(result.scalars().all())

    async def existing_concept_ids(self, user_id: int, concept_ids: list[int]) -> set[int]:
        # POST /study-plan — 이미 등록된 concept을 걸러내기 위한 조회
        if not concept_ids:
            return set()
        result = await self.db.execute(
            select(StudyPlan.conceptId).where(
                StudyPlan.userId == user_id,
                StudyPlan.conceptId.in_(concept_ids),
            )
        )
        return set(result.scalars().all())

    async def create_many(self, user_id: int, concept_ids: list[int]) -> None:
        # POST /study-plan — 신규 concept만 일괄 등록 (커밋은 서비스에서 일괄 처리)
        for concept_id in concept_ids:
            self.db.add(StudyPlan(userId=user_id, conceptId=concept_id))

    async def delete(self, user_id: int, concept_id: int) -> bool:
        # DELETE /study-plan/{conceptId} — 등록 해제. 삭제된 행이 있으면 True (커밋은 서비스에서)
        result = await self.db.execute(
            delete(StudyPlan).where(
                StudyPlan.userId == user_id,
                StudyPlan.conceptId == concept_id,
            )
        )
        return result.rowcount > 0
