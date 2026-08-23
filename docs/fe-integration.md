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

## 4. localStorage 키 목록

| 키 | 값 | 삭제 시점 |
|---|---|---|
| `cific_session_token` | 익명 세션 토큰 | merge 완료 후 |
| `cific_selected_subject_id` | 입문자가 선택한 과목 id | merge 완료 후 |

---

## 5. 에러 코드 처리

| 코드 | HTTP | FE 처리 |
|---|---|---|
| `UNAUTHORIZED` | 401 | 로그인 페이지로 리다이렉트 |
| `SESSION_TOKEN_REQUIRED` | 400 | X-Session-Token 헤더 누락 — 세션 재발급 유도 |
| `INVALID_SESSION` | 401 | 존재하지 않는 세션 — 재발급 유도 |
| `SESSION_EXPIRED` | 401 | 세션 만료 → 재발급 또는 회원가입 유도 |
| `SESSION_ALREADY_MERGED` | 409 | 무시 (이미 병합됨) |
| `SUBJECT_REQUIRED` | 400 | 과목 미선택 — 과목 선택 화면으로 이동 |
| `QUESTION_NOT_FOUND` | 404 | "문제를 찾을 수 없습니다" 토스트 |
| `INVALID_REQUEST` | 400 | 폼 유효성 오류 메시지 표시 |

---

## 6. 공통 응답 형식

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

## 7. CORS 설정

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

## 8. 개발 환경

| 항목 | 값 |
|---|---|
| BE 로컬 베이스 URL | `http://localhost:8000` |
| FE 로컬 URL (Expo Web) | `http://localhost:8081` |
| API prefix | `/api/v1` |
| Swagger UI | `http://localhost:8000/docs` |
