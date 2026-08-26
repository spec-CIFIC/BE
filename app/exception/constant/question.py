from app.exception.constant.base import ErrorCode


class QuestionErrorCode(ErrorCode):
    QUESTION_NOT_FOUND = (404, "QUESTION_NOT_FOUND", "문제를 찾을 수 없습니다.")
    INVALID_QUESTION_TYPE = (400, "INVALID_QUESTION_TYPE", "questionType은 VERBAL 또는 CALCULATION이어야 합니다.")
