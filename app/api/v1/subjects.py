from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.orm import Subject
from app.models.schemas import SubjectResponse

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("", response_model=list[SubjectResponse])
async def get_subjects(db: AsyncSession = Depends(get_db)):
    """과목 목록을 반환한다. 인증 불필요."""
    result = await db.execute(select(Subject))
    return result.scalars().all()
