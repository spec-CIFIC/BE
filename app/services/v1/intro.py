from app.exception.constant.intro import IntroErrorCode
from app.exception.constant.question import QuestionErrorCode
from app.exception.exception import CificException
from app.models.orm import AnonSession
from app.models.schemas import (
    ConceptResultItem,
    ConceptWeakItem,
    IntroAttemptRequest,
    IntroAttemptResponse,
    IntroReportResponse,
)
from app.repository.anon_session import AnonSessionRepository
from app.repository.attempt import AttemptRepository
from app.repository.concept import ConceptRepository
from app.repository.question import QuestionRepository

DIAGNOSTIC_QUESTION_LIMIT = 10


class IntroService:
    def __init__(
        self,
        anon_session_repo: AnonSessionRepository,
        question_repo: QuestionRepository,
        attempt_repo: AttemptRepository,
        concept_repo: ConceptRepository,
    ):
        self.anon_session_repo = anon_session_repo
        self.question_repo = question_repo
        self.attempt_repo = attempt_repo
        self.concept_repo = concept_repo

    async def create_session(self) -> AnonSession:
        return await self.anon_session_repo.create()

    async def select_subject(
        self, session: AnonSession, subject_id: int
    ) -> AnonSession:
        return await self.anon_session_repo.set_subject(session, subject_id)

    async def get_concepts(self, session: AnonSession) -> list:
        if session.subjectId is None:
            raise CificException(IntroErrorCode.SUBJECT_REQUIRED)
        return await self.concept_repo.find_by_subject(session.subjectId)

    async def save_self_diagnosis(
        self, session: AnonSession, weak_concept_ids: list[int]
    ) -> AnonSession:
        return await self.anon_session_repo.update_self_diagnosis(
            session, weak_concept_ids
        )

    async def get_diagnostic_questions(self, session: AnonSession) -> list:
        concept_ids: list[int] = []
        if session.self_diagnosis:
            concept_ids = session.self_diagnosis.get("weakConceptIds", [])

        if not concept_ids:
            # 약점 미선택 시: 선택 과목의 개념 전체를 대상으로 출제.
            # 과목도 없으면(예외 흐름) 전체 개념으로 폴백.
            if session.subjectId is not None:
                concepts = await self.concept_repo.find_by_subject(session.subjectId)
            else:
                concepts = await self.concept_repo.find_all()
            concept_ids = [c.id for c in concepts]

        return await self.question_repo.find_approved_by_concepts(
            concept_ids, DIAGNOSTIC_QUESTION_LIMIT
        )

    async def submit_attempt(
        self, session: AnonSession, body: IntroAttemptRequest
    ) -> IntroAttemptResponse:
        question = await self.question_repo.find_approved_by_id(body.questionId)
        if not question:
            raise CificException(QuestionErrorCode.QUESTION_NOT_FOUND)

        is_correct = body.selectedIndex == question.answerIndex

        attempt = await self.attempt_repo.create_for_anon(
            anon_session_id=session.id,
            question_id=body.questionId,
            selected_index=body.selectedIndex,
            is_correct=is_correct,
            duration_ms=body.durationMs,
        )
        return IntroAttemptResponse(
            id=attempt.id,
            isCorrect=is_correct,
            explanation=question.explanation,
        )

    async def get_report(self, session: AnonSession) -> IntroReportResponse:
        predicted_weak: list[ConceptWeakItem] = []
        if session.self_diagnosis:
            weak_ids = session.self_diagnosis.get("weakConceptIds", [])
            if weak_ids:
                concepts = await self.concept_repo.find_by_ids(weak_ids)
                predicted_weak = [
                    ConceptWeakItem(conceptId=c.id, conceptName=c.conceptName)
                    for c in concepts
                ]

        stats = await self.anon_session_repo.get_attempt_stats(session.id)
        actual_results = [
            ConceptResultItem(
                conceptId=row["conceptId"],
                conceptName=row["conceptName"],
                correct=row["correct"] or 0,
                total=row["total"],
                accuracy=round(
                    (row["correct"] or 0) / row["total"], 2
                ) if row["total"] > 0 else 0.0,
            )
            for row in stats
        ]

        return IntroReportResponse(
            predictedWeak=predicted_weak,
            actualResults=actual_results,
        )

    async def merge_session(self, session: AnonSession, user_id: int) -> None:
        if session.mergedUserId is not None:
            raise CificException(IntroErrorCode.SESSION_ALREADY_MERGED)
        await self.anon_session_repo.set_merged_user(session, user_id)
