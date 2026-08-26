# v0 — BE·FE 스켈레톤

> 로드맵 목표: 실제로 풀 수 있는 최소 형태. AI 생성·검증 파이프라인 없이 API 골격만.

## 완료 기준

- [ ] BE: 문제 조회·풀이 제출·프로필 수정 API 동작
- [ ] FE: 문제 목록 → 풀이 → 결과 화면 플로우 연결
- [ ] 로컬에서 BE↔FE 연동 확인

## BE 작업

| 상태 | 작업 |
|---|---|
| ✅ | Supabase JWT 인증 (`GET /auth/me`) |
| ✅ | 과목 목록 (`GET /subjects`) |
| ✅ | 문제 단건 조회 (`GET /questions/{id}`) |
| ✅ | 문제 목록 조회 (`GET /questions`) |
| ✅ | 풀이 제출 (`POST /attempts`) |
| ✅ | 유저 프로필 수정 (`PATCH /users/me`) |

## FE 작업

FE 레포 별도 관리 (Next.js + TypeScript)

## 남은 것

| 상태 | 작업 |
|---|---|
| ✅ | 익명 세션 발급·병합 → @.claude/plans/v0_auth.md |

## v1으로 이월

- 숙련도·오답노트 API
- 개념별 필터링 고도화
- 문제 생성·검증 파이프라인 (processors, validators)
