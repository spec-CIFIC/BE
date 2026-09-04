from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import User
from app.models.schemas import ReviewConceptItem
from app.repository.mastery import MasteryRepository


class ReviewService:
    def __init__(
        self,
        db: AsyncSession,
        mastery_repo: MasteryRepository,
    ):
        self.db = db
        self.mastery_repo = mastery_repo

    async def list_review_concepts(self, user: User) -> list[ReviewConceptItem]:
        # GET /review/concepts — 에빙하우스 복습 예정 개념 (STUDY_PLAN 먼저 → 약한 순)
        now = datetime.now(timezone.utc)
        rows = await self.mastery_repo.find_due_concepts(user.id, now)
        return [
            ReviewConceptItem(
                conceptId=row.conceptId,
                conceptName=row.conceptName,
                score=row.score,
                nextReviewAt=row.nextReviewAt,
                isStudyPlan=bool(row.is_study_plan),
            )
            for row in rows
        ]
