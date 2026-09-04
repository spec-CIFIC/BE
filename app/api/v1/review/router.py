from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_review_service
from app.models.orm import User
from app.models.schemas import ReviewConceptItem
from app.services.v1.review import ReviewService

router = APIRouter(prefix="/review", tags=["review"])


@router.get("/concepts", response_model=list[ReviewConceptItem])
async def list_review_concepts(
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    """에빙하우스 복습 예정 개념 목록(STUDY_PLAN 먼저 → 숙련도 약한 순)."""
    return await review_service.list_review_concepts(current_user)
