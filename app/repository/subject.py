from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import Subject


class SubjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_all(self) -> list[Subject]:
        result = await self.db.execute(select(Subject))
        return list(result.scalars().all())
