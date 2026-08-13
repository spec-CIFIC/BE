from fastapi import APIRouter

from app.api.v1.attempts.router import router as attempts_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.questions.router import router as questions_router
from app.api.v1.subjects.router import router as subjects_router
from app.api.v1.users.router import router as users_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(subjects_router)
api_router.include_router(questions_router)
api_router.include_router(attempts_router)
