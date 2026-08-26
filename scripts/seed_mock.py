"""Mockup 데이터 시딩 스크립트 (개발용).

- subject 여러 개 + 각 subject의 concept 5개
- 문제 유형별 각 1개씩: VERBAL(말문제), GENERATED(AI계산), PAST_EXAM(기출)
- 멱등성: stem으로 존재 확인 후 없을 때만 INSERT. 재실행해도 중복이 생기지 않는다.
- 기존 VERBAL stem 패턴 문제의 questionType을 VERBAL로 백필한다.
- 모든 문제는 status="APPROVED" (intro/questions가 APPROVED만 조회하므로).

실행:
    python scripts/seed_mock.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select, update  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.models.orm import Concept, Questions, Subject  # noqa: E402

DATA: dict[str, list[str]] = {
    "재무회계": ["감가상각", "재고자산", "금융자산", "사채", "리스"],
    "세법": ["부가가치세", "법인세", "소득세", "양도소득세", "국세기본법"],
    "원가관리회계": ["원가배분", "종합원가계산", "표준원가", "CVP분석", "예산편성"],
    "재무관리": ["화폐의시간가치", "자본예산", "포트폴리오이론", "자본구조", "옵션가치평가"],
}


def verbal_question(concept: str) -> dict:
    """말문제 — 이론·법조문 서술 판단형. questionType=VERBAL, isAiGenerated=True."""
    return {
        "stem": f"[{concept}] 다음 중 {concept}에 관한 설명으로 옳지 않은 것은?",
        "choices": [
            f"{concept}의 기본 개념에 부합하는 설명이다.",
            f"{concept}의 인식·측정 기준을 바르게 적용한 설명이다.",
            f"{concept}의 회계처리 원칙과 일치하는 설명이다.",
            f"{concept}의 기준서 규정과 명백히 어긋나는 설명이다.",
        ],
        "answerIndex": 3,
        "explanation": f"4번은 {concept} 관련 기준을 잘못 적용한 서술이므로 옳지 않다.",
        "questionType": "VERBAL",
        "isAiGenerated": True,
    }


def calc_question(concept: str) -> dict:
    """AI 생성 계산문제. questionType=CALCULATION, isAiGenerated=True."""
    return {
        "stem": (
            f"[{concept}] 다음 자료를 이용하여 계산한 금액으로 옳은 것은? "
            f"(단, {concept} 관련 기본 가정을 따른다)"
        ),
        "choices": ["100,000원", "150,000원", "200,000원", "250,000원"],
        "answerIndex": 1,
        "explanation": f"제시된 자료를 {concept} 산식에 대입하면 150,000원이 도출된다.",
        "questionType": "CALCULATION",
        "isAiGenerated": True,
    }


def past_exam_question(concept: str) -> dict:
    """기출 계산문제. questionType=CALCULATION, isAiGenerated=False."""
    return {
        "stem": (
            f"[{concept}·기출] 다음은 {concept}와 관련된 자료이다. "
            f"아래 자료에 의할 때 정답으로 옳은 것은? (CPA 기출 변형)"
        ),
        "choices": ["① 50,000원", "② 100,000원", "③ 150,000원", "④ 200,000원"],
        "answerIndex": 2,
        "explanation": (
            f"{concept} 기출 문제의 핵심은 산식의 정확한 적용이다. "
            "제시된 수치를 대입하면 ③ 150,000원이 도출된다."
        ),
        "questionType": "CALCULATION",
        "isAiGenerated": False,
    }


async def get_or_create_subject(db, name: str) -> Subject:
    row = await db.execute(select(Subject).where(Subject.subjectName == name))
    subject = row.scalar_one_or_none()
    if subject is None:
        subject = Subject(subjectName=name)
        db.add(subject)
        await db.flush()
        print(f"  + SUBJECT '{name}' 생성")
    return subject


async def get_or_create_concept(db, subject_id: int, name: str) -> Concept:
    row = await db.execute(
        select(Concept).where(
            Concept.subjectId == subject_id, Concept.conceptName == name
        )
    )
    concept = row.scalar_one_or_none()
    if concept is None:
        concept = Concept(subjectId=subject_id, conceptName=name)
        db.add(concept)
        await db.flush()
        print(f"    + CONCEPT '{name}' 생성")
    return concept


async def create_question_if_absent(db, subject_id: int, concept_id: int, q: dict) -> None:
    row = await db.execute(select(Questions).where(Questions.stem == q["stem"]))
    existing = row.scalar_one_or_none()
    if existing is not None:
        changed = False
        if existing.questionType != q["questionType"]:
            existing.questionType = q["questionType"]
            changed = True
        if existing.isAiGenerated != q["isAiGenerated"]:
            existing.isAiGenerated = q["isAiGenerated"]
            changed = True
        if changed:
            print(f"      ~ 업데이트: '{q['stem'][:30]}...'")
        return
    db.add(
        Questions(
            subjectId=subject_id,
            conceptId=concept_id,
            stem=q["stem"],
            choices=q["choices"],
            answerIndex=q["answerIndex"],
            explanation=q["explanation"],
            status="APPROVED",
            questionType=q["questionType"],
            isAiGenerated=q["isAiGenerated"],
        )
    )
    print(f"      + [{q['questionType']}|ai={q['isAiGenerated']}] '{q['stem'][:35]}...' 생성")


async def main() -> None:
    async with AsyncSessionLocal() as db:
        for subject_name, concepts in DATA.items():
            print(f"\n[{subject_name}]")
            subject = await get_or_create_subject(db, subject_name)
            for concept_name in concepts:
                concept = await get_or_create_concept(db, subject.id, concept_name)
                await create_question_if_absent(
                    db, subject.id, concept.id, verbal_question(concept_name)
                )
                await create_question_if_absent(
                    db, subject.id, concept.id, calc_question(concept_name)
                )
                await create_question_if_absent(
                    db, subject.id, concept.id, past_exam_question(concept_name)
                )
        await db.commit()
    print("\n시딩 완료.")


if __name__ == "__main__":
    asyncio.run(main())
