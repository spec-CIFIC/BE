from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_optional_user
from app.models.orm import Questions, User
from app.models.schemas import QuestionsResponse
from typing import Optional

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/{question_id}", response_model=QuestionsResponse)
async def get_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """문제 단건 조회. 익명 사용자도 접근 가능."""
    result = await db.execute(
        select(Questions).where(
            Questions.id == question_id,
            Questions.status == "APPROVED",
        )
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="문제를 찾을 수 없습니다.")
    return question
