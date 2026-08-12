from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.orm import User
from app.models.schemas import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """내 프로필을 반환한다."""
    return current_user
