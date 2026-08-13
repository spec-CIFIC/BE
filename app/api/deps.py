from typing import AsyncGenerator, Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_supabase_token
from app.db.database import AsyncSessionLocal
from app.exception.constant.common import CommonErrorCode
from app.exception.exception import CificException
from app.models.orm import User
from app.repository.attempt import AttemptRepository
from app.repository.question import QuestionRepository
from app.repository.subject import SubjectRepository
from app.repository.user import UserRepository
from app.services.attempt import AttemptService
from app.services.question import QuestionService
from app.services.subject import SubjectService
from app.services.user import UserService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# ── Repository 의존성 ──────────────────────────────────────────

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_question_repository(db: AsyncSession = Depends(get_db)) -> QuestionRepository:
    return QuestionRepository(db)


def get_attempt_repository(db: AsyncSession = Depends(get_db)) -> AttemptRepository:
    return AttemptRepository(db)


def get_subject_repository(db: AsyncSession = Depends(get_db)) -> SubjectRepository:
    return SubjectRepository(db)


# ── Service 의존성 ─────────────────────────────────────────────

def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repo)


def get_question_service(
    repo: QuestionRepository = Depends(get_question_repository),
) -> QuestionService:
    return QuestionService(repo)


def get_attempt_service(
    attempt_repo: AttemptRepository = Depends(get_attempt_repository),
    question_repo: QuestionRepository = Depends(get_question_repository),
) -> AttemptService:
    return AttemptService(attempt_repo, question_repo)


def get_subject_service(
    repo: SubjectRepository = Depends(get_subject_repository),
) -> SubjectService:
    return SubjectService(repo)


# ── 인증 의존성 ────────────────────────────────────────────────

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    user_service: UserService = Depends(get_user_service),
) -> User:
    if not credentials:
        raise CificException(CommonErrorCode.UNAUTHORIZED)
    payload = verify_supabase_token(credentials.credentials)
    return await user_service.get_or_create_from_token(payload)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    user_service: UserService = Depends(get_user_service),
) -> Optional[User]:
    if not credentials:
        return None
    try:
        payload = verify_supabase_token(credentials.credentials)
        return await user_service.get_or_create_from_token(payload)
    except CificException:
        return None
