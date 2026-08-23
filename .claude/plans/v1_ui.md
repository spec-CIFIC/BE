# v1 — 검증 3·5단계 + 문제풀이 UI

> 로드맵 목표: 검증 파이프라인 3·5단계 추가, 실제로 풀 수 있는 완성된 형태.

## 완료 기준

- [ ] 검증 3단계: 교차 검증 (다른 모델이 정답 확인)
- [ ] 검증 5단계: 기출 유사도 (임베딩 비교)
- [ ] FE: 풀이 플로우 완성 (정오 피드백, 해설 표시)
- [ ] 문제 뱅크에 검증된 문제 적재 데모 가능

## 주요 작업

- `validators/cross_validation.py` — LLM 교차 검증
- `validators/similarity_check.py` — pgvector 임베딩 유사도
- FE 문제풀이 UI 완성
- 숙련도·오답노트 API 추가

## 문제 유형(questionType) — 앱/웹 분리와 연동

> 근거: `platform_strategy.md` (앱=말문제, 웹=계산문제). 말문제는 **별도 플랜이 아니라
> `QUESTIONS`의 유형 속성**으로 다룬다.

- `QUESTIONS`에 `questionType` + `isAiGenerated` 컬럼 추가 → **완료** (feat/anon_sessions)
  - `questionType`: `VERBAL`(말문제·서술형) / `CALCULATION`(계산문제·수식 적용형)
  - `isAiGenerated`: `true`(AI 생성) / `false`(기출, 인간 출제)
  - 두 축이 독립: 기출 계산문제 = `questionType=CALCULATION, isAiGenerated=false`
- 서빙 시 필터: 말문제 진입 → `questionType=VERBAL`, 기출 진입 → `isAiGenerated=false`.
- **반복학습(오답노트·간격반복)은 유형 무관 공통** — 말문제/계산 구분 없이 동일하게 복습.
- 유의: 계산문제는 검증 2단계(코드 채점)로 신뢰도 확보가 되지만, 말문제는 그 방식이 안 통한다.
  말문제 생성·검증 신뢰도 전략은 열린 과제(`platform_strategy.md`).

## 선행 조건

- v0 완료 후 시작
- **앱/웹 분리가 선행** — 플랫폼별 문제 유형 서빙은 웹(Next.js) 분리 이후 온전해진다.
