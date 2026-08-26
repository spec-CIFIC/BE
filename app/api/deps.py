from datetime import datetime, timezone
from typing import AsyncGenerator, Optional

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_supabase_token
from app.db.database import AsyncSessionLocal
from app.exception.constant.common import CommonErrorCode
from app.exception.constant.intro import IntroErrorCode
from app.exception.exception import CificException
from app.models.orm import AnonSession, User
from app.repository.anon_session import AnonSessionRepository
from app.repository.attempt import AttemptRepository
from app.repository.concept import ConceptRepository
from app.repository.home import HomeRepository
from app.repository.mastery import MasteryRepository
from app.repository.question import QuestionRepository
from app.repository.study_plan import StudyPlanRepository
from app.repository.subject import SubjectRepository
from app.repository.user import UserRepository
from app.repository.wrongnote import WrongnoteRepository
from app.services.v1.attempt import AttemptService
from app.services.v1.home import HomeService
from app.services.v1.intro import IntroService
from app.services.v1.question import QuestionService
from app.services.v1.review import ReviewService
from app.services.v1.study_plan import StudyPlanService
from app.services.v1.subject import SubjectService
from app.services.v1.user import UserService

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


def get_mastery_repository(db: AsyncSession = Depends(get_db)) -> MasteryRepository:
    return MasteryRepository(db)


def get_wrongnote_repository(db: AsyncSession = Depends(get_db)) -> WrongnoteRepository:
    return WrongnoteRepository(db)


def get_attempt_service(
    db: AsyncSession = Depends(get_db),
    attempt_repo: AttemptRepository = Depends(get_attempt_repository),
    question_repo: QuestionRepository = Depends(get_question_repository),
    mastery_repo: MasteryRepository = Depends(get_mastery_repository),
    wrongnote_repo: WrongnoteRepository = Depends(get_wrongnote_repository),
) -> AttemptService:
    return AttemptService(db, attempt_repo, question_repo, mastery_repo, wrongnote_repo)


def get_subject_service(
    repo: SubjectRepository = Depends(get_subject_repository),
) -> SubjectService:
    return SubjectService(repo)


def get_anon_session_repository(
    db: AsyncSession = Depends(get_db),
) -> AnonSessionRepository:
    return AnonSessionRepository(db)


def get_concept_repository(db: AsyncSession = Depends(get_db)) -> ConceptRepository:
    return ConceptRepository(db)


def get_intro_service(
    anon_session_repo: AnonSessionRepository = Depends(get_anon_session_repository),
    question_repo: QuestionRepository = Depends(get_question_repository),
    attempt_repo: AttemptRepository = Depends(get_attempt_repository),
    concept_repo: ConceptRepository = Depends(get_concept_repository),
) -> IntroService:
    return IntroService(anon_session_repo, question_repo, attempt_repo, concept_repo)


def get_home_repository(db: AsyncSession = Depends(get_db)) -> HomeRepository:
    return HomeRepository(db)


def get_home_service(
    home_repo: HomeRepository = Depends(get_home_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> HomeService:
    return HomeService(home_repo, user_repo)


def get_study_plan_repository(db: AsyncSession = Depends(get_db)) -> StudyPlanRepository:
    return StudyPlanRepository(db)


def get_study_plan_service(
    db: AsyncSession = Depends(get_db),
    study_plan_repo: StudyPlanRepository = Depends(get_study_plan_repository),
    concept_repo: ConceptRepository = Depends(get_concept_repository),
) -> StudyPlanService:
    return StudyPlanService(db, study_plan_repo, concept_repo)


def get_review_service(
    db: AsyncSession = Depends(get_db),
    mastery_repo: MasteryRepository = Depends(get_mastery_repository),
    wrongnote_repo: WrongnoteRepository = Depends(get_wrongnote_repository),
) -> ReviewService:
    return ReviewService(db, mastery_repo, wrongnote_repo)


# ── 인증 의존성 ────────────────────────────────────────────────

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    user_service: UserService = Depends(get_user_service),
) -> User:
    if not credentials:
        raise CificException(CommonErrorCode.UNAUTHORIZED)
    payload = verify_supabase_token(credentials.credentials)
    return await user_service.get_from_token(payload)


async def get_anon_session(
    x_session_token: Optional[str] = Header(None, alias="X-Session-Token"),
    anon_session_repo: AnonSessionRepository = Depends(get_anon_session_repository),
) -> AnonSession:
    if not x_session_token:
        raise CificException(IntroErrorCode.SESSION_TOKEN_REQUIRED)
    session = await anon_session_repo.find_by_token(x_session_token)
    if not session:
        raise CificException(IntroErrorCode.INVALID_SESSION)
    expires_at = session.expiresAt
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise CificException(IntroErrorCode.SESSION_EXPIRED)
    return session


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    user_service: UserService = Depends(get_user_service),
) -> Optional[User]:
    if not credentials:
        return None
    try:
        payload = verify_supabase_token(credentials.credentials)
        return await user_service.get_from_token(payload)
    except CificException:
        return None
