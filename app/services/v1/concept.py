from app.models.orm import Questions, User
from app.models.schemas import ConceptListItem
from app.repository.concept import ConceptRepository
from app.repository.question import QuestionRepository


class ConceptService:
    def __init__(self, concept_repo: ConceptRepository, question_repo: QuestionRepository):
        self.concept_repo = concept_repo
        self.question_repo = question_repo

    async def list_concepts(self, user: User) -> list[ConceptListItem]:
        # GET /concepts — 유저 과목 기반 개념 목록 (STUDY_PLAN 우선 + 가나다 정렬)
        rows = await self.concept_repo.find_by_subject_with_study_plan(user.id, user.subjectId)
        return [
            ConceptListItem(
                conceptId=row.id,
                conceptName=row.conceptName,
                isStudyPlan=bool(row.is_study_plan),
            )
            for row in rows
        ]

    async def list_concept_questions(
        self, concept_id: int, limit: int, offset: int
    ) -> list[Questions]:
        # GET /concepts/{id}/questions — 개념별 전체 문제 (AI 생성 + 기출 구분 없이 반환)
        # isAiGenerated 구분은 FE에서 처리
        return await self.question_repo.find_approved(
            concept_id=concept_id,
            question_type=None,
            past_exam=False,
            limit=limit,
            offset=offset,
        )
