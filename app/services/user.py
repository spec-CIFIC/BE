from app.models.orm import User
from app.models.schemas import UserUpdate
from app.repository.user import UserRepository


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_or_create_from_token(self, payload: dict) -> User:
        supabase_uid = payload.get("sub")
        email = payload.get("email", "")
        user = await self.repo.find_by_supabase_uid(supabase_uid)
        if not user:
            user = await self.repo.create(
                supabase_uid=supabase_uid,
                email=email,
                name=email.split("@")[0],
                provider=payload.get("app_metadata", {}).get("provider", "unknown"),
            )
        return user

    async def update_profile(self, user: User, body: UserUpdate) -> User:
        return await self.repo.update(user, body.model_dump(exclude_none=True))
