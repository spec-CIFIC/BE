from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import User
from app.models.schemas import ReviewConceptItem, ReviewWrongnoteItem
from app.repository.mastery import MasteryRepository
from app.repository.wrongnote import WrongnoteRepository


class ReviewService:
    def __init__(
        self,
        db: AsyncSession,
        mastery_repo: MasteryRepository,
        wrongnote_repo: WrongnoteRepository,
    ):
        self.db = db
        self.mastery_repo = mastery_repo
        self.wrongnote_repo = wrongnote_repo

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

    async def list_review_wrongnotes(
        self, user: User, concept_id: Optional[int]
    ) -> list[ReviewWrongnoteItem]:
        # GET /review/wrongnotes — 에빙하우스 복습 예정 오답 (reviewDueAt <= now)
        # STUDY_PLAN 등록 개념 먼저 정렬, concept_id로 드릴다운 가능
        now = datetime.now(timezone.utc)
        rows = await self.wrongnote_repo.find_due(user.id, now, concept_id)
        return [
            ReviewWrongnoteItem(
                wrongnoteId=row.id,
                questionId=row.questionId,
                subjectId=row.subjectId,
                subjectName=row.subjectName,
                conceptId=row.conceptId,
                conceptName=row.conceptName,
                stem=row.stem,
                choices=row.choices,
                answerIndex=row.answerIndex,
                userAnswer=row.selectedIndex,
                explanation=row.explanation,
                mistakeType=row.mistakeType,
                userMemo=row.userMemo,
                reviewDueAt=row.reviewDueAt,
                wrongCount=row.wrongCount,
                updatedAt=row.updatedAt,
                isStudyPlan=bool(row.is_study_plan),
                isFavorited=bool(row.isFavorited),
            )
            for row in rows
        ]
