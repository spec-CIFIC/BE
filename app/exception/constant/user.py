from app.exception.constant.base import ErrorCode


class UserErrorCode(ErrorCode):
    USER_NOT_FOUND = (404, "USER_NOT_FOUND", "유저를 찾을 수 없습니다.")
