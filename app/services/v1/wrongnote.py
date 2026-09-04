from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.constant.wrongnote import WrongnoteErrorCode
from app.exception.exception import CificException
from app.models.orm import User
from app.models.schemas import ReviewWrongnoteItem
from app.repository.wrongnote import WrongnoteRepository


class WrongnoteService:
    def __init__(
        self,
        db: AsyncSession,
        wrongnote_repo: WrongnoteRepository,
    ):
        self.db = db
        self.wrongnote_repo = wrongnote_repo

    async def list_wrongnotes(
        self, user: User, concept_id: Optional[int]
    ) -> list[ReviewWrongnoteItem]:
        # GET /wrongnotes — 복습 예정 오답노트 (문제 본문 포함, concept_id로 필터 가능)
        now = datetime.now(timezone.utc)
        rows = await self.wrongnote_repo.find_due(user.id, now, concept_id)
        return [
            ReviewWrongnoteItem(
                wrongnoteId=row.id,
                questionId=row.questionId,
                conceptId=row.conceptId,
                conceptName=row.conceptName,
                stem=row.stem,
                choices=row.choices,
                answerIndex=row.answerIndex,
                userAnswer=row.selectedIndex,
                explanation=row.explanation,
                mistakeType=row.mistakeType,
                userMemo=row.userMemo,
                reviewDueAt=row.reviewDueAt,
                isStudyPlan=bool(row.is_study_plan),
                isFavorited=bool(row.isFavorited),
            )
            for row in rows
        ]

    async def list_all_wrongnotes(
        self,
        user: User,
        q: Optional[str],
        subject_id: Optional[int],
        is_favorited: Optional[bool],
    ) -> list[ReviewWrongnoteItem]:
        # GET /wrongnotes — 전체 오답노트 (검색/필터 지원)
        rows = await self.wrongnote_repo.find_all(user.id, q, subject_id, is_favorited)
        return [
            ReviewWrongnoteItem(
                wrongnoteId=row.id,
                questionId=row.questionId,
                subjectId=row.subjectId,
                subjectName=row.subjectName,
                conceptId=row.conceptId,
                conceptName=row.conceptName,
                stem=row.stem,
                choices=row.choices,
                answerIndex=row.answerIndex,
                userAnswer=row.selectedIndex,
                explanation=row.explanation,
                mistakeType=row.mistakeType,
                userMemo=row.userMemo,
                reviewDueAt=row.reviewDueAt,
                wrongCount=row.wrongCount,
                updatedAt=row.updatedAt,
                isStudyPlan=bool(row.is_study_plan),
                isFavorited=bool(row.isFavorited),
            )
            for row in rows
        ]

    async def update_memo(self, user: User, wrongnote_id: int, memo: str) -> None:
        # PATCH /wrongnotes/{id} — 오답노트 코멘트(userMemo) 저장
        wrongnote = await self.wrongnote_repo.find_by_id(user.id, wrongnote_id)
        if not wrongnote:
            raise CificException(WrongnoteErrorCode.WRONGNOTE_NOT_FOUND)
        await self.wrongnote_repo.update_memo(wrongnote, memo)
        await self.db.commit()

    async def update_favorite(
        self, user: User, wrongnote_id: int, is_favorited: bool
    ) -> None:
        # PATCH /wrongnotes/{id}/favorite — 즐겨찾기 ON/OFF 저장
        wrongnote = await self.wrongnote_repo.find_by_id(user.id, wrongnote_id)
        if not wrongnote:
            raise CificException(WrongnoteErrorCode.WRONGNOTE_NOT_FOUND)
        await self.wrongnote_repo.update_favorite(wrongnote, is_favorited)
        await self.db.commit()
