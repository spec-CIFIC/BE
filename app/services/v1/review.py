from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.constant.review import ReviewErrorCode
from app.exception.exception import CificException
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

    async def list_wrongnotes(
        self, user: User, concept_id: Optional[int]
    ) -> list[ReviewWrongnoteItem]:
        # GET /review/wrongnotes — 복습 예정 오답노트 (문제 본문 포함, concept_id로 필터 가능)
        now = datetime.now(timezone.utc)
        rows = await self.wrongnote_repo.find_due(user.id, now, concept_id)
        return [
            ReviewWrongnoteItem(
                wrongnoteId=row.id,
                questionId=row.questionId,
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
                isStudyPlan=bool(row.is_study_plan),
            )
            for row in rows
        ]

    async def update_memo(self, user: User, wrongnote_id: int, memo: str) -> None:
        # PATCH /review/wrongnotes/{id} — 오답노트 코멘트(userMemo) 저장
        wrongnote = await self.wrongnote_repo.find_by_id(user.id, wrongnote_id)
        if not wrongnote:
            raise CificException(ReviewErrorCode.WRONGNOTE_NOT_FOUND)
        await self.wrongnote_repo.update_memo(wrongnote, memo)
        await self.db.commit()
