# FE 연동 가이드

> BE 구현 기준으로 FE가 참조해야 하는 계약 문서.
> Swagger(`/docs`)는 스펙, 이 문서는 **왜 그렇게 써야 하는지**를 다룬다.
> BE API가 추가·변경될 때 함께 업데이트한다.

---

## 1. 인증 구조

### 토큰 두 종류

| 종류 | 발급처 | 저장 위치 | 용도 |
|---|---|---|---|
| `accessToken` (JWT) | Supabase Auth | 메모리 또는 httpOnly 쿠키 | 로그인 유저 API 호출 |
| `sessionToken` | `POST /api/v1/sessions` | `localStorage` | 비로그인 입문자 풀이 저장 |

### 요청 헤더 규칙

```
# 로그인 유저
Authorization: Bearer {accessToken}

# 비로그인 입문자
X-Session-Token: {sessionToken}
```

둘 다 없으면 인증이 필요한 API는 `401` 반환.

---

## 2. 첫 화면 분기 플로우

```
첫 화면
  ├── "처음 이용해요" (입문자 플로우 — /intro/*)
  │     1. POST /api/v1/intro/sessions → sessionToken 발급
  │     2. localStorage에 'cific_session_token' 키로 저장
  │     3. POST /api/v1/intro/subject { subjectId } → 시험 과목 선택 (선행)
  │        └ 선택 과목을 localStorage 'cific_selected_subject_id'에 함께 저장
  │     4. GET /api/v1/intro/concepts → 선택 과목의 개념 목록 수신
  │     5. POST /api/v1/intro/self-diagnosis → 약점 개념 선택 저장
  │     6. GET /api/v1/intro/questions → 진단 문제 10개 수신
  │     7. POST /api/v1/intro/attempts × N → 익명 풀이 제출
  │     8. GET /api/v1/intro/report → 약점 리포트 확인
  │     9. 회원가입 → Supabase Auth
  │     10. POST /api/v1/auth/register { subjectId } → 3에서 고른 과목 그대로 전달
  │     11. POST /api/v1/auth/merge → 데이터 병합 (X-Session-Token + Bearer)
  │     12. localStorage에서 세션·과목 키 삭제
  │     13. 대시보드 이동
  │
  └── "기존 회원이에요 / 회원가입"
        1. Supabase Auth 로그인 or 회원가입
        2. (신규) POST /api/v1/auth/register { subjectId } → BE 회원 레코드 생성
           (직접 가입은 회원가입 화면에서 과목을 직접 선택)
        3. accessToken으로 API 호출
        4. 대시보드 이동
```

> **과목(subject) 처리 정책 (A안)**: 익명 단계에서 선택한 과목은 `ANON_SESSION.subjectId`에 저장되고,
> FE가 이 값을 기억했다가 회원가입 시 `POST /auth/register`의 `subjectId`로 그대로 전달한다.
> `merge`는 풀이기록 연결만 담당하며 과목을 옮기지 않는다. `USER.subjectId`는 NOT NULL 유지.

---

## 3. API별 FE 사용법

### 과목 (`/subjects`)

#### `GET /api/v1/subjects` — 과목 목록

```ts
// 인증 불필요. 전체 과목 목록과 각 과목의 승인된 문제 수를 반환.
const subjects = await get('/api/v1/subjects')
// subjects: [{ id, subjectName, questionCount }]
```

---

### 프로필 (`/users/me`)

#### `GET /api/v1/users/me` — 내 프로필 조회

```ts
// Authorization: Bearer 필요.
const user = await get(
  '/api/v1/users/me',
  { headers: { Authorization: `Bearer ${accessToken}` } }
)
// user: {
//   id, email, name, subjectId,
//   provider,           // "LOCAL" | "GOOGLE" | "KAKAO" | null
//   examName,           // 목표 시험명 (미설정 시 null)
//   examDate,           // "YYYY-MM-DD" (미설정 시 null)
//   streakCount,        // 연속 학습일 수
//   weeklyAttemptCount, // 최근 7일 풀이 수
//   studyDays,          // 가입일부터 오늘까지 누적 일수
//   createdAt, updatedAt
// }
```

#### `PATCH /api/v1/users/me` — 프로필 수정

```ts
// Authorization: Bearer 필요. 모든 필드 optional — 수정할 필드만 포함.
const updated = await patch(
  '/api/v1/users/me',
  { name: '정수혁', examName: 'CPA 1차', examDate: '2026-11-01' },
  { headers: { Authorization: `Bearer ${accessToken}` } }
)
// 응답: GET /users/me와 동일한 UserResponse
```

---

### 문제 (`/questions`)

#### `GET /api/v1/questions` — 문제 목록

```ts
// 인증 선택적 (비로그인도 가능).
// concept_id 지정 시 해당 개념 문제만, filter로 특화 문제 추출.
const questions = await get(
  '/api/v1/questions?concept_id=3&filter=verbal&limit=20&offset=0'
)
// filter 값:
//   "verbal"    → 말문제 특화 (questionType=VERBAL)
//   "past_exam" → 전범위 기출 (isAiGenerated=false)
//   생략 시 전체 반환
//
// questions: [{
//   id, subjectId, conceptId, stem, choices,
//   answerIndex,    // ⚠️ 정답 인덱스 포함 — 문제 풀이 전 FE에서 숨김 처리 필수
//   explanation, questionType, isAiGenerated, createdAt
// }]
```

#### `GET /api/v1/questions/{id}` — 문제 단건 조회

```ts
// 동일 스키마. 존재하지 않는 id → 404 QUESTION_NOT_FOUND.
const question = await get(`/api/v1/questions/${questionId}`)
```

---

### 단원학습 (`/concepts/*`)

#### `GET /api/v1/concepts` — 개념 목록

```ts
// 로그인 유저의 과목(USER.subjectId) 기반 개념 목록.
// STUDY_PLAN 등록 개념 먼저, 각 그룹 내 가나다순 정렬.
const concepts = await get(
  '/api/v1/concepts',
  { headers: { Authorization: `Bearer ${accessToken}` } }
)
// concepts: [{ conceptId, conceptName, isStudyPlan }]
// isStudyPlan: true인 항목을 FE에서 시각적으로 강조
```

#### `GET /api/v1/concepts/{conceptId}/questions` — 개념별 문제 목록

```ts
// 특정 개념의 전체 문제 (AI 생성 + 기출 구분 없이 반환).
// isAiGenerated 값으로 FE에서 구분 표시.
const questions = await get(
  `/api/v1/concepts/${conceptId}/questions?limit=20&offset=0`
)
// questions: [{ id, stem, choices, answerIndex, explanation, questionType, isAiGenerated, ... }]
```

### 학습 기록 (`/attempts/*`)

#### `GET /api/v1/attempts` — 학습 기록 목록

```ts
// 로그인 유저의 학습 기록을 최근순으로 조회. limit/offset 페이지네이션.
const { items, total, limit, offset } = await get(
  '/api/v1/attempts?limit=20&offset=0',
  { headers: { Authorization: `Bearer ${accessToken}` } }
)
// items: [{
//   attemptId, isCorrect, durationMs, createdAt,
//   question: { id, stemPreview },   ← stem 최대 80자
//   concept:  { id, conceptName },
//   subject:  { id, subjectName }
// }]
```

#### `GET /api/v1/attempts/{attemptId}` — 학습 기록 상세

```ts
// 특정 attempt 상세. 본인 attempt만 접근 가능.
// 타인 attempt 또는 존재하지 않는 ID → 404 ATTEMPT_NOT_FOUND
const detail = await get(
  `/api/v1/attempts/${attemptId}`,
  { headers: { Authorization: `Bearer ${accessToken}` } }
)
// detail: {
//   attemptId, isCorrect, durationMs, selectedIndex, createdAt,
//   question: { id, stem, choices, answerIndex, explanation },
//   concept:  { id, conceptName },
//   subject:  { id, subjectName }
// }
```

### 입문자 플로우 (`/intro/*`)

#### `POST /api/v1/intro/sessions`
```ts
// 입문자 진입 시 1회 호출. 인증 헤더 불필요.
const { sessionToken, expiresAt } = await post('/api/v1/intro/sessions')
localStorage.setItem('cific_session_token', sessionToken)
```

#### `POST /api/v1/intro/subject`
```ts
// 시험 과목 선택 → 세션에 저장. 개념/문제 조회보다 선행. 204 No Content.
await post('/api/v1/intro/subject',
  { subjectId: 1 },
  { headers: { 'X-Session-Token': sessionToken } }
)
localStorage.setItem('cific_selected_subject_id', String(1))
```

#### `GET /api/v1/intro/concepts`
```ts
// 선택한 과목의 개념 목록 조회 (약점 선택 UI용).
// 과목 미선택 상태로 호출하면 400 SUBJECT_REQUIRED.
const concepts = await get('/api/v1/intro/concepts', {
  headers: { 'X-Session-Token': sessionToken }
})
// concepts: [{ id, conceptName }]
```

#### `POST /api/v1/intro/self-diagnosis`
```ts
// 약점 개념 선택 후 저장. 204 No Content 반환.
await post('/api/v1/intro/self-diagnosis',
  { weakConceptIds: [3, 7, 12] },
  { headers: { 'X-Session-Token': sessionToken } }
)
```

#### `GET /api/v1/intro/questions`
```ts
// 자가진단 기반 진단 문제 조회. answerIndex 미포함.
// 약점 미선택 시 선택 과목의 전체 개념에서 출제된다.
const questions = await get('/api/v1/intro/questions', {
  headers: { 'X-Session-Token': sessionToken }
})
```

#### `POST /api/v1/intro/attempts`
```ts
// 익명 풀이 제출. isCorrect + explanation 반환.
const { id, isCorrect, explanation } = await post(
  '/api/v1/intro/attempts',
  { questionId, selectedIndex, durationMs },
  { headers: { 'X-Session-Token': sessionToken } }
)
```

#### `GET /api/v1/intro/report`
```ts
// 예측 약점 vs 실제 결과 비교 리포트
const { predictedWeak, actualResults } = await get('/api/v1/intro/report', {
  headers: { 'X-Session-Token': sessionToken }
})
// predictedWeak: [{ conceptId, conceptName }]
// actualResults: [{ conceptId, conceptName, correct, total, accuracy }]
```

### 회원가입 / 기존 회원 플로우

#### `POST /api/v1/auth/register`
```ts
// Supabase Auth 가입 직후 1회 호출. accessToken + subjectId 필요.
await post('/api/v1/auth/register',
  { subjectId: 1 },
  { headers: { Authorization: `Bearer ${accessToken}` } }
)
```

#### `POST /api/v1/attempts`
```ts
// 로그인 유저 풀이 제출
await post('/api/v1/attempts', body, {
  headers: { Authorization: `Bearer ${accessToken}` }
})
```

### 병합

#### `POST /api/v1/auth/merge`
```ts
// 회원가입 직후 1회 호출. Bearer + X-Session-Token 둘 다 필요.
const sessionToken = localStorage.getItem('cific_session_token')
if (sessionToken) {
  await post('/api/v1/auth/merge', null, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'X-Session-Token': sessionToken,
    }
  })
  localStorage.removeItem('cific_session_token')
}
```

---

## 4. 홈화면 복습 큐 진입 조건 (STUDY_PLAN)

`GET /home` 응답에 `hasStudyPlan: boolean` 필드가 포함된다.
FE는 이 값으로 홈화면 복습 큐 영역의 렌더링을 분기한다.

```ts
const { hasStudyPlan, reviewQueue, ... } = await get('/api/v1/home', ...)

// hasStudyPlan === false → 주요 개념 등록 유도 UI
// hasStudyPlan === true  → 정상 복습 큐 표시
```

| `hasStudyPlan` | 복습 큐 영역 표시 |
|---|---|
| `false` | "학습 전략을 세워볼까요? 주요 학습 개념을 먼저 등록해주세요." + 등록 버튼 |
| `true` | 추천 복습 개념 수 + 다시 볼 오답 수 + 에빙하우스 기반 복습 큐 |

등록 버튼 클릭 시 → `POST /api/v1/study-plan` 호출 화면으로 이동.

---

## 5. 홈화면 API (`GET /api/v1/home`)

로그인 유저 전용. `Authorization: Bearer` 필요.

### 응답 타입

```ts
type HomeResponse = {
  user: {
    name: string
    streakCount: number
  }
  examGoal: {
    examName: string
    examDate: string  // "YYYY-MM-DD"
    dDay: number      // 양수: D-n, 0: D-Day, 음수: 시험 지남
  } | null            // 시험 목표 미설정 시 null
  reviewQueue: {
    reviewConceptCount: number  // 에빙하우스 복습 예정 개념 수
    wrongNoteCount: number      // 복습 예정 오답노트 수
  }
  dailyStrategy: string   // 서버가 생성하는 오늘의 학습 전략 문구
  hasStudyPlan: boolean   // 주요 개념 등록 여부 (복습 큐 렌더링 분기)
}
```

### 예시 응답

```json
// 시험 목표 설정 + 주요 개념 등록된 경우
{
  "user": { "name": "정수혁", "streakCount": 5 },
  "examGoal": { "examName": "CPA 1차", "examDate": "2026-11-01", "dDay": 67 },
  "reviewQueue": { "reviewConceptCount": 3, "wrongNoteCount": 7 },
  "dailyStrategy": "오늘 7개의 오답과 3개의 복습 예정 개념이 기다려요. 오답부터 해결해보세요.",
  "hasStudyPlan": true
}

// 시험 목표 미설정 유저
{
  "user": { "name": "정수혁", "streakCount": 0 },
  "examGoal": null,
  "reviewQueue": { "reviewConceptCount": 0, "wrongNoteCount": 0 },
  "dailyStrategy": "오늘 복습할 항목이 없어요. 새로운 문제에 도전해보세요!",
  "hasStudyPlan": false
}
```

### 렌더링 분기 요약

| 필드 | 조건 | FE 처리 |
|---|---|---|
| `examGoal` | `null` | 시험 목표 설정 유도 UI |
| `hasStudyPlan` | `false` | 주요 개념 등록 유도 UI (복습 큐 숨김) |
| `reviewQueue` | 둘 다 0 | "새 문제에 도전해보세요" 상태 표시 |
| `dailyStrategy` | 항상 존재 | 그대로 렌더링 |

> 복습 큐 렌더링 분기 상세는 **[§4. 홈화면 복습 큐 진입 조건]** 참조.

---

## 6. 주요 개념 (STUDY_PLAN) 우선 노출 정책

사용자가 집중하기로 선택한 concept은 `STUDY_PLAN`에 저장되며, 앱 전반에서 우선 노출된다.

### 적용 화면별 동작

| 화면 | BE 동작 | FE 처리 |
|---|---|---|
| 오늘의 복습 큐 | `/review/concepts` 응답에서 STUDY_PLAN concept이 먼저 정렬되어 내려옴 | 순서 그대로 렌더링 |
| 단원 학습 | 개념 목록은 순서 변경 없음 | STUDY_PLAN에 속한 concept에 별도 강조 표시 (예: 북마크 아이콘, 색상 구분) |
| 오답노트 | `/review/wrongnotes` 응답에서 STUDY_PLAN concept의 오답노트가 먼저 정렬되어 내려옴 | 순서 그대로 렌더링 |

### STUDY_PLAN 응답 형태

각 API 응답의 concept/wrongnote 객체에 `isStudyPlan: boolean` 필드가 포함된다.
FE는 이 값을 기준으로 단원 학습 화면에서 강조 표시 여부를 결정한다.

### STUDY_PLAN 등록/해제

```ts
// 주요 개념 일괄 등록 (여러 개 선택 후 한 번에 저장). 이미 등록된 concept은 무시됨.
// 존재하지 않는 conceptId 포함 시 404 STUDY_PLAN_CONCEPT_NOT_FOUND.
// 응답: 201, 갱신된 전체 목록 { items: [{ conceptId, conceptName, createdAt }] }
POST /api/v1/study-plan
{ "conceptIds": [3, 5, 8] }

// 주요 개념 해제. 등록되지 않은 concept이면 404 STUDY_PLAN_NOT_FOUND. 성공 시 204.
DELETE /api/v1/study-plan/{conceptId}

// 현재 주요 개념 목록 조회 → { items: [{ conceptId, conceptName, createdAt }] }
GET /api/v1/study-plan
```

---

## 6-1. 복습 화면 (`/review/*`)

홈 "추천 복습" 섹션(에빙하우스 기반)의 두 카드가 각각 연결된다. 모두 `Authorization: Bearer` 필요.

### `GET /api/v1/review/concepts` — 왼쪽 "다시 풀어볼 문제"

```ts
// 에빙하우스 복습 예정(nextReviewAt <= now) 개념 목록.
// STUDY_PLAN 등록 concept이 먼저, 그다음 숙련도(score) 약한 순으로 정렬되어 내려온다.
const concepts = await get('/api/v1/review/concepts', authHeader)
// concepts: [{ conceptId, conceptName, score, nextReviewAt, isStudyPlan }]
// → concept 선택 시 GET /review/wrongnotes?conceptId=... 로 드릴다운
```

### `GET /api/v1/review/wrongnotes` — 오른쪽 "다시 볼 오답"

```ts
// 복습 예정(reviewDueAt <= now) 오답노트. conceptId 쿼리로 특정 개념만 필터 가능.
// STUDY_PLAN concept의 오답이 먼저 정렬된다. 문제 본문·정답·해설까지 포함(오버레이 바로 렌더).
const notes = await get('/api/v1/review/wrongnotes?conceptId=3', authHeader)
// notes: [{ wrongnoteId, questionId, conceptId, conceptName, stem, choices,
//           answerIndex, userAnswer, explanation, mistakeType, userMemo,
//           reviewDueAt, isStudyPlan }]
// conceptId 생략 시 사용자의 전체 due 오답 반환 (FE가 concept으로 그룹핑 가능)
```

### `PATCH /api/v1/review/wrongnotes/{wrongnoteId}` — 코멘트 저장

```ts
// 오답노트 오버레이의 "코멘트 추가" → userMemo 저장/수정. 성공 시 204.
// 본인 오답노트가 아니거나 없으면 404 WRONGNOTE_NOT_FOUND.
await patch('/api/v1/review/wrongnotes/12', { userMemo: '선입선출법 기말재고 특성 재확인' }, authHeader)
```

### 오답노트 오버레이 UX (FE 렌더링 규칙)

오답노트 상세는 **페이지 이동이 아니라 현재 화면 위에 뜨는 오버레이 모달**로 표시한다.

- 우상단 **X**로 닫고 원래 화면으로 복귀 (라우팅 이동 아님).
- 문제(`stem`·`choices`)를 먼저 보여주고, **"해설 및 정답 보기" 토글**로 `answerIndex`(정답)·`explanation`(해설)을 접었다 폈다 한다.
- **"코멘트 추가"**는 `userMemo`이며 `PATCH /review/wrongnotes/{id}`로 저장한다.
- 오버레이는 `GET /review/wrongnotes` 응답 항목을 그대로 쓴다(추가 상세 조회 불필요).

### ⚠️ "다시 볼 오답" vs 하단바 "오답노트" 탭 — 진입점 2개, API 2개

**오버레이 UI 컴포넌트는 두 화면이 공유하지만, 데이터를 가져오는 API는 다르다.** 혼용 금지.

| 화면 | 데이터 범위 | API |
|---|---|---|
| 홈 "다시 볼 오답" 진입 | **복습 예정분만** (`reviewDueAt ≤ now`) | `GET /review/wrongnotes` (구현됨) |
| 하단바 "오답노트" 탭 | **전체 오답노트** (기한 무관, 훑어보기) | `GET /wrongnotes` (구현됨 — §12 참조) |

- 하단바 "오답노트" 탭에서 `GET /review/wrongnotes`를 호출하면 안 된다(복습 기한 지난 것만 나옴). 전체 목록은 `GET /wrongnotes`로 연결한다.
- 두 화면 모두 항목 클릭 시 위의 동일한 오버레이 컴포넌트를 띄운다.

---

## 7. localStorage 키 목록

| 키 | 값 | 삭제 시점 |
|---|---|---|
| `cific_session_token` | 익명 세션 토큰 | merge 완료 후 |
| `cific_selected_subject_id` | 입문자가 선택한 과목 id | merge 완료 후 |

---

## 8. 에러 코드 처리

| 코드 | HTTP | FE 처리 |
|---|---|---|
| `UNAUTHORIZED` | 401 | 로그인 페이지로 리다이렉트 |
| `SESSION_TOKEN_REQUIRED` | 400 | X-Session-Token 헤더 누락 — 세션 재발급 유도 |
| `INVALID_SESSION` | 401 | 존재하지 않는 세션 — 재발급 유도 |
| `SESSION_EXPIRED` | 401 | 세션 만료 → 재발급 또는 회원가입 유도 |
| `SESSION_ALREADY_MERGED` | 409 | 무시 (이미 병합됨) |
| `SUBJECT_REQUIRED` | 400 | 과목 미선택 — 과목 선택 화면으로 이동 |
| `QUESTION_NOT_FOUND` | 404 | "문제를 찾을 수 없습니다" 토스트 |
| `ATTEMPT_NOT_FOUND` | 404 | "학습 기록을 찾을 수 없습니다" 토스트 |
| `STUDY_PLAN_CONCEPT_NOT_FOUND` | 404 | 등록 요청에 없는 개념 포함 — 목록 새로고침 후 재시도 |
| `STUDY_PLAN_NOT_FOUND` | 404 | 이미 해제된 개념 — 목록 새로고침 |
| `WRONGNOTE_NOT_FOUND` | 404 | "오답노트를 찾을 수 없습니다" 토스트 |
| `INVALID_REQUEST` | 400 | 폼 유효성 오류 메시지 표시 |

---

## 9. 공통 응답 형식

```ts
// 성공
{ ...data }

// 실패
{
  "code": "ERROR_CODE",
  "message": "에러 메시지"
}
```

에러는 항상 `code` 필드로 분기 처리한다. `message`는 사용자에게 그대로 노출하지 않는다.

---

## 10. CORS 설정

FE는 BE와 다른 오리진(포트)에서 동작하므로 BE에 CORS 허용이 필요하다.
설정 위치: `app/main.py`의 `CORSMiddleware`.

| 항목 | 값 |
|---|---|
| 허용 오리진 (로컬) | `http://localhost:8081` (Expo Web), `http://localhost:3000` |
| 허용 메서드 | 전체 (`*`) |
| 허용 헤더 | 전체 (`*`) — `Authorization`, `X-Session-Token` 포함 |
| 자격증명 | `allow_credentials=True` |

- CORS 미설정 시 브라우저 preflight(`OPTIONS`)가 `405`로 실패해 모든 API 호출이 막힌다.
- **배포 시**: `allow_origins`에 실제 FE 도메인(AWS Amplify URL 등)을 추가한다. 와일드카드(`*`)는 `allow_credentials=True`와 함께 쓸 수 없으므로 오리진을 명시한다.
- 네이티브 앱(iOS/Android)은 브라우저가 아니므로 CORS 대상이 아니다. 웹(Expo Web)에서만 적용된다.

---

## 11. 개발 환경

| 항목 | 값 |
|---|---|
| BE 로컬 베이스 URL | `http://localhost:8000` |
| FE 로컬 URL (Expo Web) | `http://localhost:8081` |
| API prefix | `/api/v1` |
| Swagger UI | `http://localhost:8000/docs` |

---

## 12. 전체 오답노트 탭 (`/wrongnotes`)

하단바 "오답노트" 탭 전용. 복습 기한 무관하게 사용자의 **전체 오답노트**를 조회한다.
복습 예정분만 내려주는 `GET /review/wrongnotes`와 혼용 금지.

모두 `Authorization: Bearer` 필요.

### `GET /api/v1/wrongnotes` — 전체 오답노트 목록

```ts
// q: 과목명·개념명·문제 텍스트 검색 (선택)
// subjectId: 과목 필터 (선택)
// isFavorited: 즐겨찾기 필터 (선택)
const notes = await get(
  '/api/v1/wrongnotes?subjectId=1&isFavorited=true',
  { headers: { Authorization: `Bearer ${accessToken}` } }
)
// notes: [{
//   wrongnoteId, questionId,
//   subjectId, subjectName,
//   conceptId, conceptName,
//   stem, choices,
//   answerIndex,    // 정답 인덱스
//   userAnswer,     // 사용자가 선택한 인덱스 (null 가능)
//   explanation, mistakeType, userMemo,
//   reviewDueAt,    // 에빙하우스 복습 예정일 (null 가능)
//   wrongCount,     // 누적 오답 횟수
//   updatedAt,
//   isStudyPlan,    // 주요 개념 등록 여부
//   isFavorited     // 즐겨찾기 여부
// }]
```

### `PATCH /api/v1/wrongnotes/{id}` — 코멘트 저장

```ts
// userMemo 저장/수정. 성공 시 204.
// 본인 오답노트가 아니거나 없으면 404 WRONGNOTE_NOT_FOUND.
await patch(`/api/v1/wrongnotes/${wrongnoteId}`,
  { userMemo: '선입선출법 기말재고 특성 재확인' },
  { headers: { Authorization: `Bearer ${accessToken}` } }
)
```

### `PATCH /api/v1/wrongnotes/{id}/favorite` — 즐겨찾기 ON/OFF

```ts
// isFavorited true/false로 토글. 성공 시 204.
// 본인 오답노트가 아니거나 없으면 404 WRONGNOTE_NOT_FOUND.
await patch(`/api/v1/wrongnotes/${wrongnoteId}/favorite`,
  { isFavorited: true },
  { headers: { Authorization: `Bearer ${accessToken}` } }
)
```
