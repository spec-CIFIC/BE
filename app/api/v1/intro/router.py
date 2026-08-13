from fastapi import APIRouter, Depends

from app.api.deps import get_anon_session, get_intro_service
from app.models.orm import AnonSession
from app.models.schemas import (
    DiagnosticQuestionResponse,
    IntroAttemptRequest,
    IntroAttemptResponse,
    IntroReportResponse,
    IntroSessionResponse,
    SelfDiagnosisRequest,
)
from app.services.intro import IntroService

router = APIRouter(prefix="/intro", tags=["intro"])


@router.post("/sessions", response_model=IntroSessionResponse, status_code=201)
async def create_session(intro_service: IntroService = Depends(get_intro_service)):
    """익명 세션을 생성하고 sessionToken을 반환한다."""
    return await intro_service.create_session()


@router.post("/self-diagnosis", status_code=204)
async def save_self_diagnosis(
    body: SelfDiagnosisRequest,
    session: AnonSession = Depends(get_anon_session),
    intro_service: IntroService = Depends(get_intro_service),
):
    """자가진단 약점 과목을 세션에 저장한다."""
    await intro_service.save_self_diagnosis(session, body.weakConceptIds)


@router.get("/questions", response_model=list[DiagnosticQuestionResponse])
async def get_diagnostic_questions(
    session: AnonSession = Depends(get_anon_session),
    intro_service: IntroService = Depends(get_intro_service),
):
    """자가진단 기반으로 진단 문제를 반환한다."""
    return await intro_service.get_diagnostic_questions(session)


@router.post("/attempts", response_model=IntroAttemptResponse, status_code=201)
async def submit_attempt(
    body: IntroAttemptRequest,
    session: AnonSession = Depends(get_anon_session),
    intro_service: IntroService = Depends(get_intro_service),
):
    """익명 세션으로 풀이를 제출하고 정오 결과와 해설을 반환한다."""
    return await intro_service.submit_attempt(session, body)


@router.get("/report", response_model=IntroReportResponse)
async def get_report(
    session: AnonSession = Depends(get_anon_session),
    intro_service: IntroService = Depends(get_intro_service),
):
    """예측 약점 vs 실제 결과 리포트를 반환한다."""
    return await intro_service.get_report(session)
