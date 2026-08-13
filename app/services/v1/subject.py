from app.models.orm import Subject
from app.repository.subject import SubjectRepository


class SubjectService:
    def __init__(self, repo: SubjectRepository):
        self.repo = repo

    async def list_subjects(self) -> list[Subject]:
        return await self.repo.find_all()
