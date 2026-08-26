from datetime import date, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.constant.user import UserErrorCode
from app.exception.exception import CificException
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
        # IntegrityError 발생 케이스 두 가지:
        #   (1) supabase_uid 충돌 — 동시 요청 TOCTOU. 이미 생성된 유저를 재조회해 반환.
        #   (2) email 충돌 — 같은 이메일이 다른 uid로 이미 존재(예: Supabase 유저 삭제/재생성).
        #       → uid 재조회 시 없으므로 EMAIL_ALREADY_EXISTS(409)로 명시적 처리.
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
            existing = result.scalar_one_or_none()
            if existing is None:
                # uid는 안 겹치는데 INSERT가 실패 → email unique 충돌로 간주
                raise CificException(UserErrorCode.EMAIL_ALREADY_EXISTS)
            user = existing
        return user

    async def update(self, user: User, fields: dict) -> User:
        # PATCH /users/me — 변경된 필드만 setattr로 반영
        for key, value in fields.items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_streak(self, user: User) -> None:
        # POST /attempts 제출 시 호출 — 오늘 첫 번째 풀이에서만 streak 갱신
        today = date.today()
        if user.lastStudiedAt == today:
            return
        if user.lastStudiedAt == today - timedelta(days=1):
            user.streakCount += 1
        else:
            user.streakCount = 1
        user.lastStudiedAt = today
        await self.db.commit()
