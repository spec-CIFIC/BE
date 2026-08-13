from fastapi import APIRouter, Depends

from app.api.deps import get_subject_service
from app.models.schemas import SubjectResponse
from app.services.subject import SubjectService

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("", response_model=list[SubjectResponse])
async def get_subjects(subject_service: SubjectService = Depends(get_subject_service)):
    return await subject_service.list_subjects()
