# MVP ERD

자격시험 AI 학습 플랫폼 (CPA 우선) — MVP 데이터 모델.

## 개요

- 목적: 문제 출제 / 풀이 기록 / 약점 진단 / 오답노트를 지탱하는 최소 데이터 정의.
- DBMS: PostgreSQL (Supabase 호스팅). `id`는 auto-increment PK.
- 익명 사용자 지원: 로그인 전에도 문제를 풀 수 있고, 로그인 시 익명 세션을 계정에 병합한다.
- 이 문서는 확정된 MVP 스키마다. 확장 항목은 `보류/확장 예정` 섹션 참고.

> 스키마 변경 절차 및 마이그레이션 이력 → [SCHEMA_MANAGEMENT.md](./SCHEMA_MANAGEMENT.md)

## 엔티티 요약

| 테이블 | 역할 |
|---|---|
| `ANON_SESSION` | 로그인 전 익명 세션. 로그인 시 유저에 병합 |
| `USER` | 사용자 계정 |
| `SUBJECT` | 과목 (재무회계 등) |
| `CONCEPT` | 개념 (감가상각, 사채 등). 과목에 속함 |
| `QUESTIONS` | 문제. 과목·개념에 연결 |
| `ATTEMPT` | 풀이 기록. 약점/오답노트의 원천 데이터 |
| `MASTERY` | 사용자 × 개념별 숙련도 (ATTEMPT에서 산출) |
| `WRONGNOTE` | 오답노트 엔트리 |

## 관계

- `SUBJECT` 1 — N `CONCEPT`
- `SUBJECT` 1 — N `QUESTIONS`
- `CONCEPT` 1 — N `QUESTIONS`
- `USER` 1 — N `ATTEMPT`, `MASTERY`, `WRONGNOTE`
- `SUBJECT` 1 — N `ANON_SESSION` (입문자 선택 과목)
- `ANON_SESSION` 1 — N `ATTEMPT`
- `QUESTIONS` 1 — N `ATTEMPT`
- `ATTEMPT` 1 — N `WRONGNOTE`
- `CONCEPT` 1 — N `MASTERY`, `WRONGNOTE`

## 핵심 설계 결정

- `ATTEMPT.userId` / `ATTEMPT.anonSessionId`는 **둘 중 하나만 채워진다.** 익명이면 `userId`가 null, 로그인 유저면 `anonSessionId`가 null.
- 숙련도는 `USER`에 고정값으로 두지 않는다. 개념마다 다르므로 `MASTERY`에서 사용자 × 개념 조합별로 관리하고, ATTEMPT가 쌓이면 갱신한다.
- `WRONGNOTE.mistakeType`(AI가 판정한 실수 유형)과 `userMemo`(사용자 자유 메모)는 성격이 달라 분리한다.
- `QUESTIONS.status` + `trustScore`로 검증 파이프라인 결과를 저장한다. 생성 직후 `PENDING`, 5단계 통과 후 점수에 따라 `APPROVED` / `HUMAN_REVIEW` / `REJECTED`로 라우팅된다. 출제 시 `status = 'APPROVED'`인 문제만 서빙한다.

## DBML

```dbml
Table ANON_SESSION {
  id             bigint       [pk, increment]
  sessionToken   varchar(100) [unique, not null, note: '브라우저에 저장되는 임시 토큰']
  createdAt      timestamptz  [not null]
  expiresAt      timestamptz  [not null, note: '만료 시각 (7일)']
  subjectId      bigint       [null, ref: > SUBJECT.id, note: '입문자가 선택한 시험 과목 (과목→개념 선행 선택)']
  mergedUserId   bigint       [null, ref: > USER.id, note: '로그인 시 병합된 유저']
  self_diagnosis json         [null, note: '자가진단 데이터. {"weakConceptIds": [3, 7, 12]}']
}

Table USER {
  id            bigint       [pk, increment]
  supabase_uid  varchar(36)  [unique, null, note: 'Supabase auth.users.id (UUID). 로그인 시 유저 식별']
  email         varchar(100) [unique, not null]
  password      varchar(255) [null, note: '소셜 로그인 시 null 가능']
  name          varchar(50)  [not null]
  provider      varchar(20)  [null, note: 'LOCAL / GOOGLE / KAKAO']
  subjectId     bigint       [not null, ref: > SUBJECT.id, note: '회원가입 시 필수 선택']
  examName      varchar(100) [null, note: '목표 시험명 (예: 2027 CPA 1차). 홈 D-Day 카드용']
  examDate      date         [null, note: '목표 시험일. D-Day 계산 기준']
  streakCount   int          [not null, default: 0, note: '현재 연속 학습일수']
  lastStudiedAt date         [null, note: '마지막 학습일. streak 연속 여부 판단에 사용']
  createdAt     timestamptz  [not null]
  updatedAt     timestamptz  [not null]
}

Table SUBJECT {
  id          bigint       [pk, increment]
  subjectName varchar(50)  [not null]
}

Table QUESTIONS {
  id           bigint       [pk, increment]
  subjectId    bigint       [not null, ref: > SUBJECT.id]
  conceptId    bigint       [not null, ref: > CONCEPT.id]
  stem         text         [not null, note: '문제 내용']
  choices      json         [not null, note: '선택지 배열']
  answerIndex  int          [not null, note: '정답 번호']
  explanation  text         [null, note: '해설']
  questionType  varchar(20)  [not null, default: 'CALCULATION', note: 'VERBAL(말문제·서술형) / CALCULATION(계산문제·수식 적용형)']
  isAiGenerated boolean      [not null, default: true, note: 'true=AI 생성 / false=기출(인간 출제)']
  status        varchar(20)  [not null, default: 'PENDING', note: 'PENDING / APPROVED / HUMAN_REVIEW / REJECTED']
  trustScore   float        [null, note: '검증 파이프라인 종합 신뢰도 (0~1). 라우팅 기준값']
  createdAt    timestamptz  [not null]
}

Table ATTEMPT {
  id            bigint      [pk, increment]
  userId        bigint      [null, ref: > USER.id, note: '익명이면 null']
  anonSessionId bigint      [null, ref: > ANON_SESSION.id, note: '로그인 유저면 null']
  questionId    bigint      [not null, ref: > QUESTIONS.id]
  selectedIndex int         [not null, note: '사용자가 고른 번호']
  isCorrect     boolean     [not null]
  durationMs    int         [null, note: '소요 시간(ms)']
  createdAt     timestamptz [not null]
}

Table CONCEPT {
  id          bigint       [pk, increment]
  subjectId   bigint       [not null, ref: > SUBJECT.id]
  conceptName varchar(100) [not null, note: '감가상각, 사채 등']
}

Table MASTERY {
  id          bigint       [pk, increment]
  userId      bigint       [not null, ref: > USER.id]
  conceptId   bigint       [not null, ref: > CONCEPT.id]
  score       float        [not null, note: '0~1 숙련도']
  sampleSize  int          [not null, note: '표본 수, 진단 신뢰도용']
  updatedAt   timestamptz  [not null]
}

Table WRONGNOTE {
  id          bigint       [pk, increment]
  userId      bigint       [not null, ref: > USER.id]
  attemptId   bigint       [not null, ref: > ATTEMPT.id]
  conceptId   bigint       [not null, ref: > CONCEPT.id]
  mistakeType text         [null, note: '실수 유형: 잔존가치_누락 등 (AI 판정)']
  userMemo    text         [null, note: '사용자가 해당 문제에 직접 쓰는 메모']
  reviewDueAt timestamptz  [null, note: '복습 시점(간격 반복용)']
}
```

## 보류 / 확장 예정

MVP에서 제외한 항목. 근거와 함께 남겨 나중에 판단한다.

- `QUESTIONS.difficulty` — 난이도. 지금은 정할 근거가 없고 적응형 출제는 후순위라 제외. 필요 시 컬럼 추가.
- `QUESTIONS.solutionCode` — 검증(계산 코드 실행)용. 검증 파이프라인 구현 단계에서 추가.
- `CONCEPT.parentUnit` — 개념 상위 단원(유형자산 등). 개념 taxonomy를 전문가 지식베이스로 제대로 짤 때 도입.
- 문제별 체류 시간 정밀 기록(`VIEW_EVENT`류) — 재진입/수정까지 반영한 이벤트 단위 시간 기록. 별도 논의 예정. 현재는 `ATTEMPT.durationMs`(nullable, 약한 신호)로만.
- `WRONGNOTE.mistakeType` 정규화 — 현재 text. 실수 유형 사전(enum/별도 테이블)으로 승격 여지 있음.