from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_review_service
from app.models.orm import User
from app.models.schemas import (
    ReviewConceptItem,
    ReviewWrongnoteItem,
    WrongnoteMemoUpdateRequest,
)
from app.services.v1.review import ReviewService

router = APIRouter(prefix="/review", tags=["review"])


@router.get("/concepts", response_model=list[ReviewConceptItem])
async def list_review_concepts(
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    """에빙하우스 복습 예정 개념 목록(STUDY_PLAN 먼저 → 숙련도 약한 순)."""
    return await review_service.list_review_concepts(current_user)


@router.get("/wrongnotes", response_model=list[ReviewWrongnoteItem])
async def list_review_wrongnotes(
    conceptId: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    """복습 예정 오답노트 목록. conceptId를 주면 해당 개념으로 필터."""
    return await review_service.list_wrongnotes(current_user, conceptId)


@router.patch("/wrongnotes/{wrongnote_id}", status_code=204)
async def update_wrongnote_memo(
    wrongnote_id: int,
    body: WrongnoteMemoUpdateRequest,
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    """오답노트 코멘트(메모)를 저장/수정한다."""
    await review_service.update_memo(current_user, wrongnote_id, body.userMemo)
