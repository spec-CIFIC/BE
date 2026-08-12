from app.exception.constant.base import ErrorCode


class AuthErrorCode(ErrorCode):
    EXPIRED_TOKEN = (401, "EXPIRED_TOKEN", "토큰이 만료되었습니다.")
    INVALID_TOKEN = (401, "INVALID_TOKEN", "유효하지 않은 토큰입니다.")
