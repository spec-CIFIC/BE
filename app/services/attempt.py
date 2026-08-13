from app.exception.constant.attempt import AttemptErrorCode
from app.exception.exception import CificException
from app.models.orm import Attempt, User
from app.models.schemas import AttemptBase
from app.repository.attempt import AttemptRepository
from app.repository.question import QuestionRepository


class AttemptService:
    def __init__(
        self,
        attempt_repo: AttemptRepository,
        question_repo: QuestionRepository,
    ):
        self.attempt_repo = attempt_repo
        self.question_repo = question_repo

    async def submit(self, user: User, body: AttemptBase) -> Attempt:
        question = await self.question_repo.find_approved_by_id(body.questionId)
        if not question:
            raise CificException(AttemptErrorCode.QUESTION_NOT_FOUND)
        is_correct = body.selectedIndex == question.answerIndex
        return await self.attempt_repo.create(
            user_id=user.id,
            question_id=body.questionId,
            selected_index=body.selectedIndex,
            is_correct=is_correct,
            duration_ms=body.durationMs,
        )
