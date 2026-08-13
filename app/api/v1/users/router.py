from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_user_service
from app.models.orm import User
from app.models.schemas import UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_profile(current_user, body)
