"""
GET /questions?filter= 필터 로직 단위 테스트

검증 대상: QuestionService.list_questions 에서
  - filter 값에 따라 repo.find_approved 에 올바른 인자가 전달되는지
  - 잘못된 filter 값에 대해 INVALID_FILTER 예외가 발생하는지
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exception.exception import CificException
from app.services.v1.question import QuestionService


def run(coro):
    return asyncio.run(coro)


def make_service():
    repo = MagicMock()
    repo.find_approved = AsyncMock(return_value=[])
    return QuestionService(repo=repo), repo


# ── filter=verbal ──────────────────────────────────────────────────────────────

def test_filter_verbal_sets_question_type_and_past_exam():
    svc, repo = make_service()
    run(svc.list_questions(None, None, "verbal", 20, 0))
    _, kwargs = repo.find_approved.call_args
    args = repo.find_approved.call_args.args
    # find_approved(subject_id, concept_id, question_type, past_exam, limit, offset)
    assert args[2] == "VERBAL"   # question_type
    assert args[3] is True       # past_exam


# ── filter=past_exam ───────────────────────────────────────────────────────────

def test_filter_past_exam_sets_no_type_but_past_exam():
    svc, repo = make_service()
    run(svc.list_questions(None, None, "past_exam", 20, 0))
    args = repo.find_approved.call_args.args
    assert args[2] is None       # question_type — 전범위이므로 타입 제한 없음
    assert args[3] is True       # past_exam


# ── filter=None (필터 없음) ────────────────────────────────────────────────────

def test_no_filter_returns_all_including_ai():
    svc, repo = make_service()
    run(svc.list_questions(None, None, None, 20, 0))
    args = repo.find_approved.call_args.args
    assert args[2] is None       # question_type
    assert args[3] is False      # past_exam — AI 생성 포함 전체


# ── 잘못된 filter 값 ────────────────────────────────────────────────────────────

def test_invalid_filter_raises_exception():
    svc, _ = make_service()
    with pytest.raises(CificException) as exc_info:
        run(svc.list_questions(None, None, "invalid_value", 20, 0))
    assert exc_info.value.error_code.code == "INVALID_FILTER"
