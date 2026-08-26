from app.exception.constant.base import ErrorCode


class ReviewErrorCode(ErrorCode):
    WRONGNOTE_NOT_FOUND = (404, "WRONGNOTE_NOT_FOUND", "오답노트를 찾을 수 없습니다.")
