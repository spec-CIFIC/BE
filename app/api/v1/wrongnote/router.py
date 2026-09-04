from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_wrongnote_service
from app.models.orm import User
from app.models.schemas import (
    ReviewWrongnoteItem,
    WrongnoteFavoriteUpdateRequest,
    WrongnoteMemoUpdateRequest,
)
from app.services.v1.wrongnote import WrongnoteService

router = APIRouter(prefix="/wrongnotes", tags=["wrongnotes"])


@router.get("", response_model=list[ReviewWrongnoteItem])
async def list_wrongnotes(
    q: Optional[str] = Query(None),
    subjectId: Optional[int] = Query(None),
    isFavorited: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    wrongnote_service: WrongnoteService = Depends(get_wrongnote_service),
):
    """전체 오답노트 목록. q로 과목·개념·문제 텍스트 검색, subjectId로 과목 필터, isFavorited로 즐겨찾기 필터."""
    return await wrongnote_service.list_all_wrongnotes(current_user, q, subjectId, isFavorited)


@router.patch("/{wrongnote_id}", status_code=204)
async def update_wrongnote_memo(
    wrongnote_id: int,
    body: WrongnoteMemoUpdateRequest,
    current_user: User = Depends(get_current_user),
    wrongnote_service: WrongnoteService = Depends(get_wrongnote_service),
):
    """오답노트 코멘트(메모)를 저장/수정한다."""
    await wrongnote_service.update_memo(current_user, wrongnote_id, body.userMemo)


@router.patch("/{wrongnote_id}/favorite", status_code=204)
async def update_wrongnote_favorite(
    wrongnote_id: int,
    body: WrongnoteFavoriteUpdateRequest,
    current_user: User = Depends(get_current_user),
    wrongnote_service: WrongnoteService = Depends(get_wrongnote_service),
):
    """오답노트 즐겨찾기를 ON/OFF한다."""
    await wrongnote_service.update_favorite(current_user, wrongnote_id, body.isFavorited)
