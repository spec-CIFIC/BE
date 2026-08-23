import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import AnonSession, Attempt, Concept, Questions


class AnonSessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self) -> AnonSession:
        # POST /intro/sessions — 익명 세션 발급
        now = datetime.now(timezone.utc)
        session = AnonSession(
            sessionToken=str(uuid.uuid4()),
            createdAt=now,
            expiresAt=now + timedelta(days=7),
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def find_by_token(self, token: str) -> Optional[AnonSession]:
        # 모든 익명 세션 의존 엔드포인트(자가진단, 문제 조회, 풀이 제출, 리포트, 병합)에서 호출
        result = await self.db.execute(
            select(AnonSession).where(AnonSession.sessionToken == token)
        )
        return result.scalar_one_or_none()

    async def set_subject(
        self, session: AnonSession, subject_id: int
    ) -> AnonSession:
        # POST /intro/subject — 입문자가 선택한 시험 과목을 세션에 저장
        session.subjectId = subject_id
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def update_self_diagnosis(
        self, session: AnonSession, weak_concept_ids: list[int]
    ) -> AnonSession:
        # POST /intro/self-diagnosis — 자가진단 약점 개념 ID 저장
        session.self_diagnosis = {"weakConceptIds": weak_concept_ids}
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def set_merged_user(self, session: AnonSession, user_id: int) -> AnonSession:
        # POST /auth/merge — 익명 세션을 로그인한 회원과 연결
        session.mergedUserId = user_id
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_attempt_stats(self, session_id: int) -> list[dict]:
        # GET /intro/report — 익명 세션 풀이 기록을 개념별로 집계
        stmt = (
            select(
                Concept.id.label("conceptId"),
                Concept.conceptName,
                func.count(Attempt.id).label("total"),
                func.sum(
                    case((Attempt.isCorrect == True, 1), else_=0)  # noqa: E712
                ).label("correct"),
            )
            .join(Questions, Attempt.questionId == Questions.id)
            .join(Concept, Questions.conceptId == Concept.id)
            .where(Attempt.anonSessionId == session_id)
            .group_by(Concept.id, Concept.conceptName)
        )
        result = await self.db.execute(stmt)
        return [dict(row) for row in result.mappings().all()]
