from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_optional_user, get_question_service
from app.models.orm import User
from app.models.schemas import QuestionsResponse
from app.services.question import QuestionService

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", response_model=list[QuestionsResponse])
async def get_questions(
    subject_id: Optional[int] = Query(None),
    concept_id: Optional[int] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _current_user: Optional[User] = Depends(get_optional_user),
    question_service: QuestionService = Depends(get_question_service),
):
    return await question_service.list_questions(subject_id, concept_id, limit, offset)


@router.get("/{question_id}", response_model=QuestionsResponse)
async def get_question(
    question_id: int,
    _current_user: Optional[User] = Depends(get_optional_user),
    question_service: QuestionService = Depends(get_question_service),
):
    return await question_service.get_question(question_id)
