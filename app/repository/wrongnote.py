from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import Attempt, Concept, Questions, StudyPlan, Subject, Wrongnote


class WrongnoteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert(self, user_id: int, question_id: int, concept_id: int) -> None:
        # POST /attempts 오답 시 호출
        # (userId, questionId)가 이미 있으면 reviewDueAt만 리셋, 없으면 INSERT
        now = datetime.now(timezone.utc)
        review_due_at = now + timedelta(days=1)
        stmt = (
            pg_insert(Wrongnote)
            .values(
                userId=user_id,
                questionId=question_id,
                conceptId=concept_id,
                reviewDueAt=review_due_at,
                updatedAt=now,
            )
            .on_conflict_do_update(
                constraint="uq_wrongnote_user_question",
                set_={
                    "reviewDueAt": review_due_at,
                    "wrongCount": Wrongnote.wrongCount + 1,
                    "updatedAt": now,
                },
            )
        )
        await self.db.execute(stmt)

    async def find_due(
        self, user_id: int, now: datetime, concept_id: Optional[int] = None
    ) -> list[tuple]:
        # GET /wrongnotes — 복습 예정(reviewDueAt <= now) 오답노트를 문제 본문과 함께 조회
        # concept_id가 주어지면 해당 개념으로 필터. STUDY_PLAN concept을 먼저 정렬.
        # userAnswer: 해당 문제의 가장 최근 오답 attempt selectedIndex를 correlated subquery로 조회
        latest_selected = (
            select(Attempt.selectedIndex)
            .where(
                Attempt.userId == user_id,
                Attempt.questionId == Wrongnote.questionId,
                Attempt.isCorrect == False,  # noqa: E712
            )
            .order_by(Attempt.createdAt.desc())
            .limit(1)
            .correlate(Wrongnote)
            .scalar_subquery()
        )
        stmt = (
            select(
                Wrongnote.id,
                Wrongnote.questionId,
                Wrongnote.conceptId,
                Concept.conceptName,
                Questions.stem,
                Questions.choices,
                Questions.answerIndex,
                latest_selected.label("selectedIndex"),
                Questions.explanation,
                Wrongnote.mistakeType,
                Wrongnote.userMemo,
                Wrongnote.reviewDueAt,
                Wrongnote.isFavorited,
                StudyPlan.id.isnot(None).label("is_study_plan"),
            )
            .join(Questions, Questions.id == Wrongnote.questionId)
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

    async def find_all(
        self,
        user_id: int,
        q: Optional[str] = None,
        subject_id: Optional[int] = None,
        is_favorited: Optional[bool] = None,
    ) -> list[tuple]:
        # GET /wrongnotes — 전체 오답노트 (검색/필터 지원). STUDY_PLAN concept 우선 정렬.
        latest_selected = (
            select(Attempt.selectedIndex)
            .where(
                Attempt.userId == user_id,
                Attempt.questionId == Wrongnote.questionId,
                Attempt.isCorrect == False,  # noqa: E712
            )
            .order_by(Attempt.createdAt.desc())
            .limit(1)
            .correlate(Wrongnote)
            .scalar_subquery()
        )
        stmt = (
            select(
                Wrongnote.id,
                Wrongnote.questionId,
                Questions.subjectId,
                Subject.subjectName,
                Wrongnote.conceptId,
                Concept.conceptName,
                Questions.stem,
                Questions.choices,
                Questions.answerIndex,
                latest_selected.label("selectedIndex"),
                Questions.explanation,
                Wrongnote.mistakeType,
                Wrongnote.userMemo,
                Wrongnote.reviewDueAt,
                Wrongnote.wrongCount,
                Wrongnote.updatedAt,
                Wrongnote.isFavorited,
                StudyPlan.id.isnot(None).label("is_study_plan"),
            )
            .join(Questions, Questions.id == Wrongnote.questionId)
            .join(Subject, Subject.id == Questions.subjectId)
            .join(Concept, Concept.id == Wrongnote.conceptId)
            .outerjoin(
                StudyPlan,
                (StudyPlan.conceptId == Wrongnote.conceptId)
                & (StudyPlan.userId == user_id),
            )
            .where(Wrongnote.userId == user_id)
        )
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Questions.stem.ilike(pattern),
                    Concept.conceptName.ilike(pattern),
                    Subject.subjectName.ilike(pattern),
                )
            )
        if subject_id is not None:
            stmt = stmt.where(Questions.subjectId == subject_id)
        if is_favorited is not None:
            stmt = stmt.where(Wrongnote.isFavorited == is_favorited)
        stmt = stmt.order_by(StudyPlan.id.is_(None), Wrongnote.reviewDueAt.desc())
        result = await self.db.execute(stmt)
        return list(result.all())

    async def find_by_id(self, user_id: int, wrongnote_id: int) -> Optional[Wrongnote]:
        # PATCH /wrongnotes/{id} — 소유자 검증용 단건 조회
        result = await self.db.execute(
            select(Wrongnote).where(
                Wrongnote.id == wrongnote_id,
                Wrongnote.userId == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def update_memo(self, wrongnote: Wrongnote, memo: str) -> None:
        # PATCH /wrongnotes/{id} — 코멘트(userMemo) 저장 (커밋은 서비스에서)
        wrongnote.userMemo = memo

    async def update_favorite(self, wrongnote: Wrongnote, is_favorited: bool) -> None:
        # PATCH /wrongnotes/{id}/favorite — 즐겨찾기 ON/OFF 저장 (커밋은 서비스에서)
        wrongnote.isFavorited = is_favorited
