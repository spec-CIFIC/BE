from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.constant.attempt import AttemptErrorCode
from app.exception.exception import CificException
from app.models.orm import Attempt, User
from app.models.schemas import AttemptBase
from app.repository.attempt import AttemptRepository
from app.repository.mastery import MasteryRepository
from app.repository.question import QuestionRepository
from app.repository.wrongnote import WrongnoteRepository


class AttemptService:
    def __init__(
        self,
        db: AsyncSession,
        attempt_repo: AttemptRepository,
        question_repo: QuestionRepository,
        mastery_repo: MasteryRepository,
        wrongnote_repo: WrongnoteRepository,
    ):
        self.db = db
        self.attempt_repo = attempt_repo
        self.question_repo = question_repo
        self.mastery_repo = mastery_repo
        self.wrongnote_repo = wrongnote_repo

    async def submit(self, user: User, body: AttemptBase) -> Attempt:
        question = await self.question_repo.find_approved_by_id(body.questionId)
        if not question:
            raise CificException(AttemptErrorCode.QUESTION_NOT_FOUND)
        is_correct = body.selectedIndex == question.answerIndex
        # attempt·mastery·wrongnote 쓰기는 각 repository에서 커밋하지 않고,
        # 여기서 한 번만 커밋해 하나의 트랜잭션으로 묶는다 (부분 커밋 방지).
        attempt = await self.attempt_repo.create(
            user_id=user.id,
            question_id=body.questionId,
            selected_index=body.selectedIndex,
            is_correct=is_correct,
            duration_ms=body.durationMs,
        )
        await self.mastery_repo.upsert(user.id, question.conceptId, is_correct)
        if not is_correct:
            await self.wrongnote_repo.upsert(user.id, question.id, question.conceptId)
        await self.db.commit()
        return attempt
