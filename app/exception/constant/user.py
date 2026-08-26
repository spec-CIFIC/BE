from app.exception.constant.base import ErrorCode


class UserErrorCode(ErrorCode):
    USER_NOT_FOUND = (404, "USER_NOT_FOUND", "유저를 찾을 수 없습니다.")
    EMAIL_ALREADY_EXISTS = (409, "EMAIL_ALREADY_EXISTS", "이미 사용 중인 이메일입니다.")
