from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_study_plan_service
from app.models.orm import User
from app.models.schemas import StudyPlanCreateRequest, StudyPlanListResponse
from app.services.v1.study_plan import StudyPlanService

router = APIRouter(prefix="/study-plan", tags=["study-plan"])


@router.get("", response_model=StudyPlanListResponse)
async def list_study_plan(
    current_user: User = Depends(get_current_user),
    study_plan_service: StudyPlanService = Depends(get_study_plan_service),
):
    """등록된 주요 개념 목록을 조회한다."""
    return await study_plan_service.list(current_user)


@router.post("", response_model=StudyPlanListResponse, status_code=201)
async def register_study_plan(
    body: StudyPlanCreateRequest,
    current_user: User = Depends(get_current_user),
    study_plan_service: StudyPlanService = Depends(get_study_plan_service),
):
    """주요 개념을 일괄 등록한다(이미 등록된 개념은 무시)."""
    return await study_plan_service.register(current_user, body.conceptIds)


@router.delete("/{concept_id}", status_code=204)
async def unregister_study_plan(
    concept_id: int,
    current_user: User = Depends(get_current_user),
    study_plan_service: StudyPlanService = Depends(get_study_plan_service),
):
    """주요 개념 등록을 해제한다."""
    await study_plan_service.unregister(current_user, concept_id)
