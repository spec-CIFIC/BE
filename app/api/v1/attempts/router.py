from fastapi import APIRouter, Depends

from app.api.deps import get_attempt_service, get_current_user
from app.models.orm import User
from app.models.schemas import AttemptBase, AttemptResponse
from app.services.attempt import AttemptService

router = APIRouter(prefix="/attempts", tags=["attempts"])


@router.post("", response_model=AttemptResponse, status_code=201)
async def submit_attempt(
    body: AttemptBase,
    current_user: User = Depends(get_current_user),
    attempt_service: AttemptService = Depends(get_attempt_service),
):
    return await attempt_service.submit(current_user, body)
