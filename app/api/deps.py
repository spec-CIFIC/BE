from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_supabase_token
from app.db.database import AsyncSessionLocal
from app.models.orm import User

# Authorization: Bearer <token> 헤더에서 토큰을 추출한다.
# auto_error=False: 토큰이 없어도 에러를 내지 않음 (익명 허용 엔드포인트용)
bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """JWT를 검증하고 USER 테이블의 유저를 반환한다.

    첫 로그인 시 USER 테이블에 레코드가 없으면 자동 생성한다.
    토큰이 없거나 유효하지 않으면 401을 반환한다.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_supabase_token(credentials.credentials)
    supabase_uid = payload.get("sub")
    email = payload.get("email", "")

    # USER 테이블에서 supabase_uid로 조회
    result = await db.execute(select(User).where(User.supabase_uid == supabase_uid))
    user = result.scalar_one_or_none()

    # 첫 로그인 시 자동 생성
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
    """토큰이 있으면 유저를 반환하고, 없으면 None을 반환한다.

    익명 사용자도 접근 가능한 엔드포인트에서 사용한다.
    """
    if not credentials:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
