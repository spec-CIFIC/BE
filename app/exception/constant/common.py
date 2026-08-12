from app.exception.constant.base import ErrorCode


class CommonErrorCode(ErrorCode):
    UNAUTHORIZED          = (401, "UNAUTHORIZED",          "인증이 필요합니다.")
    FORBIDDEN             = (403, "FORBIDDEN",             "접근 권한이 없습니다.")
    INVALID_REQUEST       = (400, "INVALID_REQUEST",       "요청 값이 올바르지 않습니다.")
    INTERNAL_SERVER_ERROR = (500, "INTERNAL_SERVER_ERROR", "서버 내부 오류가 발생했습니다.")
