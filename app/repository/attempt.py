from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import Attempt


class AttemptRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: int,
        question_id: int,
        selected_index: int,
        is_correct: bool,
        duration_ms: int | None,
    ) -> Attempt:
        # POST /attempts — 풀이 제출마다 호출, 정오 판정 결과를 포함해 저장
        attempt = Attempt(
            userId=user_id,
            questionId=question_id,
            selectedIndex=selected_index,
            isCorrect=is_correct,
            durationMs=duration_ms,
        )
        self.db.add(attempt)
        await self.db.commit()
        await self.db.refresh(attempt)
        return attempt
