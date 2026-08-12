from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.exceptions import register_exception_handlers

app = FastAPI(
    title="CIFIC API",
    description="자격시험 AI 학습 플랫폼 — CPA 우선",
    version="0.1.0",
)

register_exception_handlers(app)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
