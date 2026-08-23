from datetime import date

from app.models.orm import User
from app.models.schemas import (
    HomeExamGoal,
    HomeResponse,
    HomeReviewQueue,
    HomeUserInfo,
)
from app.repository.home import HomeRepository
from app.repository.user import UserRepository


class HomeService:
    def __init__(self, home_repo: HomeRepository, user_repo: UserRepository):
        self.home_repo = home_repo
        self.user_repo = user_repo

    async def get_home(self, user: User) -> HomeResponse:
        await self.user_repo.update_streak(user)

        exam_goal = None
        if user.examName and user.examDate:
            d_day = (user.examDate - date.today()).days
            exam_goal = HomeExamGoal(
                examName=user.examName,
                examDate=user.examDate,
                dDay=d_day,
            )

        concept_count = await self.home_repo.count_weak_concepts(user.id)
        wrong_count = await self.home_repo.count_due_wrongnotes(user.id)

        return HomeResponse(
            user=HomeUserInfo(name=user.name, streakCount=user.streakCount),
            examGoal=exam_goal,
            reviewQueue=HomeReviewQueue(
                reviewConceptCount=concept_count,
                wrongNoteCount=wrong_count,
            ),
            dailyStrategy=self._strategy(concept_count, wrong_count),
        )

    def _strategy(self, concept_count: int, wrong_count: int) -> str:
        if wrong_count > 0 and concept_count > 0:
            return (
                f"오늘 {wrong_count}개의 오답과 {concept_count}개의 취약 개념이 복습을 기다려요. "
                "오답부터 해결해보세요."
            )
        if wrong_count > 0:
            return f"오늘 {wrong_count}개의 오답이 복습을 기다리고 있어요. 복습 큐부터 시작해보세요."
        if concept_count > 0:
            return f"{concept_count}개 개념의 숙련도가 낮아요. 오늘 복습으로 끌어올려 보세요."
        return "오늘 복습할 항목이 없어요. 새로운 문제에 도전해보세요!"
