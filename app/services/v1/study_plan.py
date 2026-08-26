from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.constant.study_plan import StudyPlanErrorCode
from app.exception.exception import CificException
from app.models.orm import User
from app.models.schemas import StudyPlanItem, StudyPlanListResponse
from app.repository.concept import ConceptRepository
from app.repository.study_plan import StudyPlanRepository


class StudyPlanService:
    def __init__(
        self,
        db: AsyncSession,
        study_plan_repo: StudyPlanRepository,
        concept_repo: ConceptRepository,
    ):
        self.db = db
        self.study_plan_repo = study_plan_repo
        self.concept_repo = concept_repo

    async def register(self, user: User, concept_ids: list[int]) -> StudyPlanListResponse:
        # POST /study-plan — 여러 개념을 일괄 등록. 유효성 검사 후 중복 제외분만 저장.
        unique_ids = list(dict.fromkeys(concept_ids))  # 요청 내 중복 제거(순서 유지)
        if unique_ids:
            found = await self.concept_repo.find_by_ids(unique_ids)
            if len(found) != len(unique_ids):
                raise CificException(StudyPlanErrorCode.STUDY_PLAN_CONCEPT_NOT_FOUND)
            already = await self.study_plan_repo.existing_concept_ids(user.id, unique_ids)
            to_add = [cid for cid in unique_ids if cid not in already]
            if to_add:
                await self.study_plan_repo.create_many(user.id, to_add)
                await self.db.commit()
        return await self.list(user)

    async def unregister(self, user: User, concept_id: int) -> None:
        # DELETE /study-plan/{conceptId} — 등록 해제
        deleted = await self.study_plan_repo.delete(user.id, concept_id)
        if not deleted:
            raise CificException(StudyPlanErrorCode.STUDY_PLAN_NOT_FOUND)
        await self.db.commit()

    async def list(self, user: User) -> StudyPlanListResponse:
        # GET /study-plan — 등록된 주요 개념 목록
        plans = await self.study_plan_repo.list_by_user(user.id)
        items = [
            StudyPlanItem(
                conceptId=plan.conceptId,
                conceptName=plan.concept.conceptName,
                createdAt=plan.createdAt,
            )
            for plan in plans
        ]
        return StudyPlanListResponse(items=items)
