from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_concept_service, get_current_user, get_optional_user
from app.models.orm import User
from app.models.schemas import ConceptListItem, QuestionsResponse
from app.services.v1.concept import ConceptService

router = APIRouter(prefix="/concepts", tags=["concepts"])


@router.get("", response_model=list[ConceptListItem])
async def list_concepts(
    current_user: User = Depends(get_current_user),
    concept_service: ConceptService = Depends(get_concept_service),
):
    return await concept_service.list_concepts(current_user)


@router.get("/{concept_id}/questions", response_model=list[QuestionsResponse])
async def list_concept_questions(
    concept_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _current_user: Optional[User] = Depends(get_optional_user),
    concept_service: ConceptService = Depends(get_concept_service),
):
    return await concept_service.list_concept_questions(concept_id, limit, offset)
