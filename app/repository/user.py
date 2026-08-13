from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_supabase_uid(self, supabase_uid: str) -> Optional[User]:
        # 모든 인증 요청마다 호출 — supabase_uid는 unique 인덱스라 O(1)
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
        subject_id: int,
    ) -> User:
        # POST /auth/register — 회원가입 시 최초 1회 호출 (subjectId 필수)
        # 동시 요청으로 같은 supabase_uid가 중복 INSERT되면 IntegrityError 발생
        # → 충돌 시 이미 생성된 유저를 재조회해 반환 (TOCTOU 방어)
        user = User(
            supabase_uid=supabase_uid,
            email=email,
            name=name,
            provider=provider,
            subjectId=subject_id,
        )
        self.db.add(user)
        try:
            await self.db.commit()
            await self.db.refresh(user)
        except IntegrityError:
            await self.db.rollback()
            result = await self.db.execute(
                select(User).where(User.supabase_uid == supabase_uid)
            )
            user = result.scalar_one()
        return user

    async def update(self, user: User, fields: dict) -> User:
        # PATCH /users/me — 변경된 필드만 setattr로 반영
        for key, value in fields.items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user
