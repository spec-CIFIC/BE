from typing import Optional

from app.exception.constant.question import QuestionErrorCode
from app.exception.exception import CificException
from app.models.orm import Questions
from app.repository.question import QuestionRepository


class QuestionService:
    def __init__(self, repo: QuestionRepository):
        self.repo = repo

    VALID_QUESTION_TYPES = {"VERBAL", "CALCULATION"}

    async def list_questions(
        self,
        subject_id: Optional[int],
        concept_id: Optional[int],
        question_type: Optional[str],
        limit: int,
        offset: int,
    ) -> list[Questions]:
        if question_type is not None and question_type not in self.VALID_QUESTION_TYPES:
            raise CificException(QuestionErrorCode.INVALID_QUESTION_TYPE)
        return await self.repo.find_approved(subject_id, concept_id, question_type, limit, offset)

    async def get_question(self, question_id: int) -> Questions:
        question = await self.repo.find_approved_by_id(question_id)
        if not question:
            raise CificException(QuestionErrorCode.QUESTION_NOT_FOUND)
        return question
