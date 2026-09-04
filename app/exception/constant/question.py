from app.exception.constant.base import ErrorCode


class QuestionErrorCode(ErrorCode):
    QUESTION_NOT_FOUND = (404, "QUESTION_NOT_FOUND", "문제를 찾을 수 없습니다.")
    INVALID_FILTER = (400, "INVALID_FILTER", "filter는 verbal 또는 past_exam만 허용됩니다.")
