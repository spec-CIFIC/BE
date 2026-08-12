from typing import AsyncGenerator, Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CificException, UnauthorizedException
from app.core.security import verify_supabase_token
from app.db.database import AsyncSessionLocal
from app.models.orm import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise UnauthorizedException("인증이 필요합니다.")

    payload = verify_supabase_token(credentials.credentials)
    supabase_uid = payload.get("sub")
    email = payload.get("email", "")

    result = await db.execute(select(User).where(User.supabase_uid == supabase_uid))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            supabase_uid=supabase_uid,
            email=email,
            name=email.split("@")[0],
            provider=payload.get("app_metadata", {}).get("provider", "unknown"),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not credentials:
        return None
    try:
        return await get_current_user(credentials, db)
    except CificException:
        return None
