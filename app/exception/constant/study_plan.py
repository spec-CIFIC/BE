from app.exception.constant.base import ErrorCode


class StudyPlanErrorCode(ErrorCode):
    STUDY_PLAN_CONCEPT_NOT_FOUND = (404, "STUDY_PLAN_CONCEPT_NOT_FOUND", "존재하지 않는 개념이 포함되어 있습니다.")
    STUDY_PLAN_NOT_FOUND = (404, "STUDY_PLAN_NOT_FOUND", "등록된 주요 개념이 아닙니다.")
