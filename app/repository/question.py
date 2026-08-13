from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import Questions


class QuestionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_approved(
        self,
        subject_id: Optional[int],
        concept_id: Optional[int],
        limit: int,
        offset: int,
    ) -> list[Questions]:
        stmt = select(Questions).where(Questions.status == "APPROVED")
        if subject_id is not None:
            stmt = stmt.where(Questions.subjectId == subject_id)
        if concept_id is not None:
            stmt = stmt.where(Questions.conceptId == concept_id)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def find_approved_by_id(self, question_id: int) -> Optional[Questions]:
        result = await self.db.execute(
            select(Questions).where(
                Questions.id == question_id,
                Questions.status == "APPROVED",
            )
        )
        return result.scalar_one_or_none()
