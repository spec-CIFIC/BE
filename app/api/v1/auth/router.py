from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.orm import User
from app.models.schemas import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """현재 로그인한 유저 정보를 반환한다."""
    return current_user
