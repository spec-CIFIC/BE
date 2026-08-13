from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_supabase_uid(self, supabase_uid: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.supabase_uid == supabase_uid)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        supabase_uid: str,
        email: str,
        name: str,
        provider: str,
    ) -> User:
        user = User(
            supabase_uid=supabase_uid,
            email=email,
            name=name,
            provider=provider,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User, fields: dict) -> User:
        for key, value in fields.items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user
