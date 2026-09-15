from app.models.schemas import SubjectResponse
from app.repository.subject import SubjectRepository


class SubjectService:
    def __init__(self, repo: SubjectRepository):
        self.repo = repo

    async def list_subjects(self) -> list[SubjectResponse]:
        # GET /subjects — 과목 목록 + 문제 수 반환
        rows = await self.repo.find_all_with_question_count()
        return [
            SubjectResponse(
                id=row.id,
                subjectName=row.subjectName,
                questionCount=row.questionCount,
            )
            for row in rows
        ]
