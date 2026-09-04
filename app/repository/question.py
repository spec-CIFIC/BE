from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import Questions


class QuestionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_approved(
        self,
        subject_id: Optional[int],
        concept_id: Optional[int],
        question_type: Optional[str],
        past_exam: bool,
        limit: int,
        offset: int,
    ) -> list[Questions]:
        # GET /questions 목록 조회 — 과목·개념·유형·출처 필터 + 페이지네이션
        # order_by(id): ORDER BY 없으면 offset 기반 페이지네이션 결과가 비결정적
        stmt = select(Questions).where(Questions.status == "APPROVED")
        if subject_id is not None:
            stmt = stmt.where(Questions.subjectId == subject_id)
        if concept_id is not None:
            stmt = stmt.where(Questions.conceptId == concept_id)
        if question_type is not None:
            stmt = stmt.where(Questions.questionType == question_type)
        if past_exam:
            stmt = stmt.where(Questions.isAiGenerated == False)  # noqa: E712
        stmt = stmt.order_by(Questions.id).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def find_approved_by_concepts(
        self, concept_ids: list[int], limit: int
    ) -> list[Questions]:
        # GET /intro/questions — 자가진단 개념 기반 진단 문제 랜덤 조회
        if not concept_ids:
            return []
        stmt = (
            select(Questions)
            .where(
                Questions.status == "APPROVED",
                Questions.conceptId.in_(concept_ids),
            )
            .order_by(func.random())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def find_approved_by_id(self, question_id: int) -> Optional[Questions]:
        # GET /questions/{id} 단건 조회, POST /attempts 제출 전 문제 검증에서 호출
        # PK 조회 후 status 필터 — APPROVED 아닌 문제는 존재해도 없는 것으로 처리
        result = await self.db.execute(
            select(Questions).where(
                Questions.id == question_id,
                Questions.status == "APPROVED",
            )
        )
        return result.scalar_one_or_none()
