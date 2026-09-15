from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import STEM_PREVIEW_LENGTH

from app.exception.constant.attempt import AttemptErrorCode
from app.exception.exception import CificException
from app.models.orm import Attempt, User
from app.models.schemas import (
    AttemptBase,
    AttemptHistoryConceptSummary,
    AttemptHistoryDetail,
    AttemptHistoryItem,
    AttemptHistoryListResponse,
    AttemptHistoryQuestionDetail,
    AttemptHistoryQuestionSummary,
    AttemptHistorySubjectSummary,
)
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
        else:
            wrongnote = await self.wrongnote_repo.find_by_question(user.id, question.id)
            if wrongnote:
                await self.wrongnote_repo.advance_review(wrongnote)
        await self.db.commit()
        return attempt

    async def list_attempts(
        self, user: User, limit: int, offset: int
    ) -> AttemptHistoryListResponse:
        # GET /attempts — 로그인 사용자의 학습 기록 목록 (최근순, 페이지네이션)
        rows, total = await self.attempt_repo.find_all_by_user(user.id, limit, offset)
        items = [
            AttemptHistoryItem(
                attemptId=row.id,
                isCorrect=row.isCorrect,
                durationMs=row.durationMs,
                createdAt=row.createdAt,
                question=AttemptHistoryQuestionSummary(
                    id=row.questionId,
                    stemPreview=row.stem[:STEM_PREVIEW_LENGTH],
                ),
                concept=AttemptHistoryConceptSummary(
                    id=row.conceptId,
                    conceptName=row.conceptName,
                ),
                subject=AttemptHistorySubjectSummary(
                    id=row.subjectId,
                    subjectName=row.subjectName,
                ),
            )
            for row in rows
        ]
        return AttemptHistoryListResponse(
            items=items, total=total, limit=limit, offset=offset
        )

    async def get_attempt_detail(
        self, user: User, attempt_id: int
    ) -> AttemptHistoryDetail:
        # GET /attempts/{attempt_id} — 본인 attempt 상세 (타인 접근 → 404로 존재 여부 미노출)
        row = await self.attempt_repo.find_by_id_with_question(attempt_id, user.id)
        if row is None:
            raise CificException(AttemptErrorCode.ATTEMPT_NOT_FOUND)
        return AttemptHistoryDetail(
            attemptId=row.id,
            isCorrect=row.isCorrect,
            durationMs=row.durationMs,
            selectedIndex=row.selectedIndex,
            createdAt=row.createdAt,
            question=AttemptHistoryQuestionDetail(
                id=row.questionId,
                stem=row.stem,
                choices=row.choices,
                answerIndex=row.answerIndex,
                explanation=row.explanation,
            ),
            concept=AttemptHistoryConceptSummary(
                id=row.conceptId,
                conceptName=row.conceptName,
            ),
            subject=AttemptHistorySubjectSummary(
                id=row.subjectId,
                subjectName=row.subjectName,
            ),
        )
