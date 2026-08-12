import jwt

from app.core.config import settings
from app.core.exceptions import ExpiredTokenException, InvalidTokenException


def verify_supabase_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenException("토큰이 만료되었습니다.")
    except jwt.InvalidTokenError:
        raise InvalidTokenException("유효하지 않은 토큰입니다.")
