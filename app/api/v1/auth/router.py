from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.deps import (
    get_anon_session,
    get_current_user,
    get_intro_service,
    get_user_service,
)
from app.core.security import verify_supabase_token
from app.models.orm import AnonSession, User
from app.models.schemas import RegisterRequest, UserResponse
from app.services.intro import IntroService
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """현재 로그인한 유저 정보를 반환한다."""
    return current_user


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    body: RegisterRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_service: UserService = Depends(get_user_service),
):
    """Supabase Auth 가입 후 subjectId를 포함해 회원 레코드를 생성한다."""
    from app.exception.constant.common import CommonErrorCode
    from app.exception.exception import CificException
    if not credentials:
        raise CificException(CommonErrorCode.UNAUTHORIZED)
    payload = verify_supabase_token(credentials.credentials)
    return await user_service.register(payload, body.subjectId)


@router.post("/merge", status_code=200)
async def merge_session(
    current_user: User = Depends(get_current_user),
    session: AnonSession = Depends(get_anon_session),
    intro_service: IntroService = Depends(get_intro_service),
):
    """입문자 익명 세션 데이터를 로그인한 회원에 병합한다."""
    await intro_service.merge_session(session, current_user.id)
    return {"message": "익명 세션이 성공적으로 병합되었습니다."}
