from datetime import date

from app.exception.constant.common import CommonErrorCode
from app.exception.exception import CificException
from app.models.orm import User
from app.models.schemas import UserResponse, UserUpdate
from app.repository.attempt import AttemptRepository
from app.repository.user import UserRepository


class UserService:
    def __init__(self, repo: UserRepository, attempt_repo: AttemptRepository):
        self.repo = repo
        self.attempt_repo = attempt_repo

    async def get_from_token(self, payload: dict) -> User:
        supabase_uid = payload.get("sub")
        user = await self.repo.find_by_supabase_uid(supabase_uid)
        if not user:
            raise CificException(CommonErrorCode.UNAUTHORIZED)
        return user

    async def get_profile(self, user: User) -> UserResponse:
        # GET /users/me — 프로필 조회 (weeklyAttemptCount, studyDays 포함)
        weekly_count = await self.attempt_repo.count_weekly_by_user(user.id)
        study_days = (date.today() - user.createdAt.date()).days
        return UserResponse.model_validate(
            {**user.__dict__, "weeklyAttemptCount": weekly_count, "studyDays": study_days}
        )

    async def register(self, payload: dict, subject_id: int) -> User:
        supabase_uid = payload.get("sub")
        email = payload.get("email", "")
        return await self.repo.create(
            supabase_uid=supabase_uid,
            email=email,
            name=email.split("@")[0],
            provider=payload.get("app_metadata", {}).get("provider", "unknown"),
            subject_id=subject_id,
        )

    async def update_profile(self, user: User, body: UserUpdate) -> UserResponse:
        # PATCH /users/me — 프로필 수정 후 weeklyAttemptCount 포함 반환
        updated = await self.repo.update(user, body.model_dump(exclude_none=True))
        return await self.get_profile(updated)
