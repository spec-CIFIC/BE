from fastapi import HTTPException, status
import jwt

from app.core.config import settings


def verify_supabase_token(token: str) -> dict:
    """Supabase JWT를 검증하고 payload를 반환한다.

    Supabase는 HS256으로 서명된 JWT를 발급한다.
    payload에는 sub(유저 UUID), email, role 등이 담겨 있다.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
