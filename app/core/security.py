import jwt

from app.core.config import settings
from app.exception.constant.auth import AuthErrorCode
from app.exception.exception import CificException


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
        raise CificException(AuthErrorCode.EXPIRED_TOKEN)
    except jwt.InvalidTokenError:
        raise CificException(AuthErrorCode.INVALID_TOKEN)
