# v2 — 검증 4단계 + 신뢰도 라우팅 + eval/골드셋

> 로드맵 목표: 자동 승인율 % 측정 가능한 수준.

## 완료 기준

- [ ] 검증 4단계: 근거 대조 (RAG + entailment)
- [ ] 신뢰도 점수 기반 라우팅 (高→자동승인, 中→검수, 低→폐기)
- [ ] 골드셋 구축 및 eval 지표 측정
- [ ] 자동 승인율 대시보드

## 주요 작업

- `validators/reference_check.py` — RAG 근거 대조
- `processors/reliability_router.py` — 신뢰도 라우팅
- eval 파이프라인 + 골드셋 데이터셋
- 관리자 검수 UI (사람 검수 큐)

## 선행 조건

v1 완료 후 시작
