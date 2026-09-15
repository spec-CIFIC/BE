from app.exception.constant.base import ErrorCode


class AttemptErrorCode(ErrorCode):
    QUESTION_NOT_FOUND = (404, "QUESTION_NOT_FOUND", "문제를 찾을 수 없습니다.")
    ATTEMPT_NOT_FOUND  = (404, "ATTEMPT_NOT_FOUND",  "학습 기록을 찾을 수 없습니다.")
