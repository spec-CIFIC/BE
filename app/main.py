from fastapi import FastAPI

from app.api.v1.router import api_router

app = FastAPI(
    title="CIFIC API",
    description="자격시험 AI 학습 플랫폼 — CPA 우선",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
