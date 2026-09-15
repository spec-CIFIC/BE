from fastapi import APIRouter

from app.api.v1.attempts.router import router as attempts_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.concepts.router import router as concepts_router
from app.api.v1.home.router import router as home_router
from app.api.v1.intro.router import router as intro_router
from app.api.v1.questions.router import router as questions_router
from app.api.v1.review.router import router as review_router
from app.api.v1.study_plan.router import router as study_plan_router
from app.api.v1.subjects.router import router as subjects_router
from app.api.v1.users.router import router as users_router
from app.api.v1.wrongnote.router import router as wrongnote_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(subjects_router)
api_router.include_router(questions_router)
api_router.include_router(attempts_router)
api_router.include_router(concepts_router)
api_router.include_router(intro_router)
api_router.include_router(home_router)
api_router.include_router(study_plan_router)
api_router.include_router(review_router)
api_router.include_router(wrongnote_router)
