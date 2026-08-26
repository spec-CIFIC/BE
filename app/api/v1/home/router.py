from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_home_service
from app.models.orm import User
from app.models.schemas import HomeResponse
from app.services.v1.home import HomeService

router = APIRouter(prefix="/home", tags=["home"])


@router.get("", response_model=HomeResponse)
async def get_home(
    current_user: User = Depends(get_current_user),
    home_service: HomeService = Depends(get_home_service),
):
    """홈화면 데이터를 집계해 반환한다."""
    return await home_service.get_home(current_user)
