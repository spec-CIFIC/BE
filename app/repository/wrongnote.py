from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import REVIEW_INTERVALS_DAYS
from app.models.orm import Attempt, Concept, Questions, StudyPlan, Subject, Wrongnote


def _next_interval_days(wrongnote: Wrongnote) -> int:
    # reviewDueAt - updatedAt으로 현재 단계를 역산해 다음 인터벌 반환
    current_days = max(
        round((wrongnote.reviewDueAt - wrongnote.updatedAt).total_seconds() / 86400), 0
    )
    for i, interval in enumerate(REVIEW_INTERVALS_DAYS):
        if current_days <= interval:
            return REVIEW_INTERVALS_DAYS[min(i + 1, len(REVIEW_INTERVALS_DAYS) - 1)]
    return REVIEW_INTERVALS_DAYS[-1]


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
        # GET /review/wrongnotes — 복습 예정(reviewDueAt <= now) 오답노트를 문제 본문과 함께 조회
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

    async def find_by_question(self, user_id: int, question_id: int) -> Optional[Wrongnote]:
        # POST /attempts 정답 시 에빙하우스 인터벌 연장을 위한 wrongnote 조회
        result = await self.db.execute(
            select(Wrongnote).where(
                Wrongnote.userId == user_id,
                Wrongnote.questionId == question_id,
            )
        )
        return result.scalar_one_or_none()

    async def advance_review(self, wrongnote: Wrongnote) -> None:
        # POST /attempts 정답 시 호출 — 다음 에빙하우스 인터벌로 reviewDueAt 연장
        # updatedAt을 갱신해 다음 역산 기준점을 최신화
        # 커밋하지 않음 — AttemptService에서 일괄 커밋
        now = datetime.now(timezone.utc)
        days = _next_interval_days(wrongnote)
        wrongnote.reviewDueAt = now + timedelta(days=days)
        wrongnote.updatedAt = now

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
