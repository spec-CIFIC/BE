from app.exception.constant.base import ErrorCode


class IntroErrorCode(ErrorCode):
    SESSION_TOKEN_REQUIRED = (400, "SESSION_TOKEN_REQUIRED", "세션 토큰이 필요합니다.")
    INVALID_SESSION = (401, "INVALID_SESSION", "유효하지 않은 세션입니다.")
    SESSION_EXPIRED = (401, "SESSION_EXPIRED", "세션이 만료되었습니다.")
    SESSION_ALREADY_MERGED = (409, "SESSION_ALREADY_MERGED", "이미 병합된 세션입니다.")
