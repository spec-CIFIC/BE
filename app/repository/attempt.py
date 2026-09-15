from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import Attempt, Concept, Questions, Subject


class AttemptRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: int,
        question_id: int,
        selected_index: int,
        is_correct: bool,
        duration_ms: int | None,
    ) -> Attempt:
        # POST /attempts — 풀이 제출마다 호출, 정오 판정 결과를 포함해 저장
        attempt = Attempt(
            userId=user_id,
            questionId=question_id,
            selectedIndex=selected_index,
            isCorrect=is_correct,
            durationMs=duration_ms,
        )
        self.db.add(attempt)
        # 커밋하지 않고 flush만 — 같은 요청 내 mastery/wrongnote 쓰기와 한 트랜잭션으로 묶기 위함.
        # 커밋은 호출자(AttemptService.submit)가 마지막에 한 번만 수행한다.
        await self.db.flush()
        await self.db.refresh(attempt)
        return attempt

    async def find_all_by_user(
        self, user_id: int, limit: int, offset: int
    ) -> tuple[list, int]:
        # GET /attempts — 로그인 사용자의 학습 기록 최근순 목록 (페이지네이션)
        count_stmt = (
            select(func.count())
            .where(Attempt.userId == user_id)
            .select_from(Attempt)
        )
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = (
            select(
                Attempt.id,
                Attempt.isCorrect,
                Attempt.durationMs,
                Attempt.createdAt,
                Questions.id.label("questionId"),
                Questions.stem,
                Concept.id.label("conceptId"),
                Concept.conceptName,
                Subject.id.label("subjectId"),
                Subject.subjectName,
            )
            .join(Questions, Questions.id == Attempt.questionId)
            .join(Concept, Concept.id == Questions.conceptId)
            .join(Subject, Subject.id == Questions.subjectId)
            .where(Attempt.userId == user_id)
            .order_by(Attempt.createdAt.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = list((await self.db.execute(stmt)).all())
        return rows, total

    async def find_by_id_with_question(
        self, attempt_id: int, user_id: int
    ) -> Optional[tuple]:
        # GET /attempts/{attempt_id} — 소유자 검증 포함 단건 상세
        # Attempt.userId == user_id 조건으로 타인 attempt는 None 반환 → ATTEMPT_NOT_FOUND 처리
        stmt = (
            select(
                Attempt.id,
                Attempt.isCorrect,
                Attempt.durationMs,
                Attempt.selectedIndex,
                Attempt.createdAt,
                Questions.id.label("questionId"),
                Questions.stem,
                Questions.choices,
                Questions.answerIndex,
                Questions.explanation,
                Concept.id.label("conceptId"),
                Concept.conceptName,
                Subject.id.label("subjectId"),
                Subject.subjectName,
            )
            .join(Questions, Questions.id == Attempt.questionId)
            .join(Concept, Concept.id == Questions.conceptId)
            .join(Subject, Subject.id == Questions.subjectId)
            .where(Attempt.id == attempt_id, Attempt.userId == user_id)
        )
        return (await self.db.execute(stmt)).one_or_none()

    async def create_for_anon(
        self,
        anon_session_id: int,
        question_id: int,
        selected_index: int,
        is_correct: bool,
        duration_ms: int | None,
    ) -> Attempt:
        # POST /intro/attempts — 익명 세션 풀이 제출
        attempt = Attempt(
            anonSessionId=anon_session_id,
            questionId=question_id,
            selectedIndex=selected_index,
            isCorrect=is_correct,
            durationMs=duration_ms,
        )
        self.db.add(attempt)
        await self.db.commit()
        await self.db.refresh(attempt)
        return attempt
