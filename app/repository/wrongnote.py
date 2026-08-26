from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import Attempt, Concept, Questions, StudyPlan, Wrongnote


class WrongnoteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, attempt_id: int, concept_id: int) -> None:
        # POST /attempts 오답 시 호출 — 에빙하우스 1회차: reviewDueAt = 지금 + 1일
        wrongnote = Wrongnote(
            userId=user_id,
            attemptId=attempt_id,
            conceptId=concept_id,
            reviewDueAt=datetime.now(timezone.utc) + timedelta(days=1),
        )
        self.db.add(wrongnote)
        # 커밋하지 않음 — attempt·mastery와 한 트랜잭션으로 묶어 호출자가 일괄 커밋한다.

    async def find_due(
        self, user_id: int, now: datetime, concept_id: Optional[int] = None
    ) -> list[tuple]:
        # GET /review/wrongnotes — 복습 예정(reviewDueAt <= now) 오답노트를 문제 본문과 함께 조회
        # concept_id가 주어지면 해당 개념으로 필터. STUDY_PLAN concept을 먼저 정렬.
        stmt = (
            select(
                Wrongnote.id,
                Attempt.questionId,
                Wrongnote.conceptId,
                Concept.conceptName,
                Questions.stem,
                Questions.choices,
                Questions.answerIndex,
                Attempt.selectedIndex,
                Questions.explanation,
                Wrongnote.mistakeType,
                Wrongnote.userMemo,
                Wrongnote.reviewDueAt,
                StudyPlan.id.isnot(None).label("is_study_plan"),
            )
            .join(Attempt, Attempt.id == Wrongnote.attemptId)
            .join(Questions, Questions.id == Attempt.questionId)
            .join(Concept, Concept.id == Wrongnote.conceptId)
            .outerjoin(
                StudyPlan,
                (StudyPlan.conceptId == Wrongnote.conceptId)
                & (StudyPlan.userId == user_id),
            )
            .where(
                Wrongnote.userId == user_id,
                Wrongnote.reviewDueAt <= now,
            )
        )
        if concept_id is not None:
            stmt = stmt.where(Wrongnote.conceptId == concept_id)
        stmt = stmt.order_by(StudyPlan.id.is_(None), Wrongnote.reviewDueAt.asc())
        result = await self.db.execute(stmt)
        return list(result.all())

    async def find_by_id(self, user_id: int, wrongnote_id: int) -> Optional[Wrongnote]:
        # PATCH /review/wrongnotes/{id} — 소유자 검증용 단건 조회
        result = await self.db.execute(
            select(Wrongnote).where(
                Wrongnote.id == wrongnote_id,
                Wrongnote.userId == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def update_memo(self, wrongnote: Wrongnote, memo: str) -> None:
        # PATCH /review/wrongnotes/{id} — 코멘트(userMemo) 저장 (커밋은 서비스에서)
        wrongnote.userMemo = memo
