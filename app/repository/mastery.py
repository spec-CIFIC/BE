from datetime import datetime, timedelta, timezone

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import Concept, Mastery, StudyPlan

EMA_ALPHA = 0.3

# 에빙하우스 간격 반복: reviewStage별 다음 복습까지의 일 수
REVIEW_INTERVALS_DAYS = [1, 3, 7, 14, 30]


def _next_schedule(prev_stage: int, is_correct: bool) -> tuple[int, datetime]:
    # 정답이면 단계 +1(상한 고정), 오답이면 0으로 리셋 → 해당 단계 간격만큼 뒤로 예약
    if is_correct:
        stage = min(prev_stage + 1, len(REVIEW_INTERVALS_DAYS) - 1)
    else:
        stage = 0
    next_review_at = datetime.now(timezone.utc) + timedelta(days=REVIEW_INTERVALS_DAYS[stage])
    return stage, next_review_at


class MasteryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert(self, user_id: int, concept_id: int, is_correct: bool) -> None:
        # POST /attempts 제출마다 호출 — EMA로 숙련도 갱신 + 에빙하우스 복습 일정 재예약
        result = await self.db.execute(
            select(Mastery).where(
                Mastery.userId == user_id,
                Mastery.conceptId == concept_id,
            )
        )
        mastery = result.scalar_one_or_none()
        current = 1.0 if is_correct else 0.0

        if mastery is None:
            # 신규는 이전 단계 -1 기준 → 첫 시도는 정오답 무관 1일 뒤 복습
            stage, next_review_at = _next_schedule(-1, is_correct)
            self.db.add(Mastery(
                userId=user_id,
                conceptId=concept_id,
                score=current,
                sampleSize=1,
                reviewStage=stage,
                nextReviewAt=next_review_at,
            ))
        else:
            mastery.score = EMA_ALPHA * current + (1 - EMA_ALPHA) * mastery.score
            mastery.sampleSize += 1
            mastery.reviewStage, mastery.nextReviewAt = _next_schedule(
                mastery.reviewStage, is_correct
            )
        # 커밋하지 않음 — attempt·wrongnote와 한 트랜잭션으로 묶어 호출자가 일괄 커밋한다.

    async def find_due_concepts(self, user_id: int, now: datetime) -> list[tuple]:
        # GET /review/concepts — 에빙하우스 복습 예정(nextReviewAt <= now 또는 null)인 개념
        # STUDY_PLAN 등록 concept을 먼저(정렬), 그다음 숙련도가 낮은 순으로 반환
        result = await self.db.execute(
            select(
                Mastery.conceptId,
                Concept.conceptName,
                Mastery.score,
                Mastery.nextReviewAt,
                StudyPlan.id.isnot(None).label("is_study_plan"),
            )
            .join(Concept, Concept.id == Mastery.conceptId)
            .outerjoin(
                StudyPlan,
                (StudyPlan.conceptId == Mastery.conceptId)
                & (StudyPlan.userId == user_id),
            )
            .where(
                Mastery.userId == user_id,
                or_(Mastery.nextReviewAt <= now, Mastery.nextReviewAt.is_(None)),
            )
            .order_by(StudyPlan.id.is_(None), Mastery.score.asc())
        )
        return list(result.all())
