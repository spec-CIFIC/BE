from fastapi import APIRouter, Depends, Query

from app.api.deps import get_attempt_service, get_current_user
from app.models.orm import User
from app.models.schemas import (
    AttemptBase,
    AttemptHistoryDetail,
    AttemptHistoryListResponse,
    AttemptResponse,
)
from app.services.v1.attempt import AttemptService

router = APIRouter(prefix="/attempts", tags=["attempts"])


@router.post("", response_model=AttemptResponse, status_code=201)
async def submit_attempt(
    body: AttemptBase,
    current_user: User = Depends(get_current_user),
    attempt_service: AttemptService = Depends(get_attempt_service),
):
    return await attempt_service.submit(current_user, body)


@router.get("", response_model=AttemptHistoryListResponse)
async def list_attempts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    attempt_service: AttemptService = Depends(get_attempt_service),
):
    return await attempt_service.list_attempts(current_user, limit, offset)


@router.get("/{attempt_id}", response_model=AttemptHistoryDetail)
async def get_attempt_detail(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    attempt_service: AttemptService = Depends(get_attempt_service),
):
    return await attempt_service.get_attempt_detail(current_user, attempt_id)
