from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_optional_user
from app.exception.constant.question import QuestionErrorCode
from app.exception.exception import CificException
from app.models.orm import Questions, User
from app.models.schemas import QuestionsResponse

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/{question_id}", response_model=QuestionsResponse)
async def get_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: Optional[User] = Depends(get_optional_user),
):
    result = await db.execute(
        select(Questions).where(
            Questions.id == question_id,
            Questions.status == "APPROVED",
        )
    )
    question = result.scalar_one_or_none()
    if not question:
        raise CificException(QuestionErrorCode.QUESTION_NOT_FOUND)
    return question
