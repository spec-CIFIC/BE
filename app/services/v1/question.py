from typing import Optional

from app.exception.constant.question import QuestionErrorCode
from app.exception.exception import CificException
from app.models.orm import Questions
from app.repository.question import QuestionRepository


class QuestionService:
    def __init__(self, repo: QuestionRepository):
        self.repo = repo

    VALID_FILTERS = {"verbal", "past_exam"}

    async def list_questions(
        self,
        subject_id: Optional[int],
        concept_id: Optional[int],
        filter: Optional[str],
        limit: int,
        offset: int,
    ) -> list[Questions]:
        # GET /questions — 문제 목록 조회
        # filter=verbal: 말문제(VERBAL)만 반환
        # filter=past_exam: 기출(isAiGenerated=false)만 반환
        if filter is not None and filter not in self.VALID_FILTERS:
            raise CificException(QuestionErrorCode.INVALID_FILTER)
        # 두 filter 값 모두 기출(isAiGenerated=false) 기반
        # verbal: 기출 중 말문제만 / past_exam: 기출 전범위(말+계산)
        question_type = "VERBAL" if filter == "verbal" else None
        past_exam = filter is not None
        return await self.repo.find_approved(subject_id, concept_id, question_type, past_exam, limit, offset)

    async def get_question(self, question_id: int) -> Questions:
        # GET /questions/{id} — 문제 단건 조회
        question = await self.repo.find_approved_by_id(question_id)
        if not question:
            raise CificException(QuestionErrorCode.QUESTION_NOT_FOUND)
        return question
