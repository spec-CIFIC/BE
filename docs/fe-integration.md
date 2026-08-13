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
  │     3. POST /api/v1/intro/self-diagnosis → 약점 과목 선택 저장
  │     4. GET /api/v1/intro/questions → 진단 문제 10개 수신
  │     5. POST /api/v1/intro/attempts × N → 익명 풀이 제출
  │     6. GET /api/v1/intro/report → 약점 리포트 확인
  │     7. 회원가입 → Supabase Auth
  │     8. POST /api/v1/auth/merge → 데이터 병합 (X-Session-Token + Bearer)
  │     9. localStorage에서 'cific_session_token' 삭제
  │     10. 대시보드 이동
  │
  └── "기존 회원이에요 / 회원가입"
        1. Supabase Auth 로그인 or 회원가입
        2. (신규) POST /api/v1/auth/register { subjectId } → BE 회원 레코드 생성
        3. accessToken으로 API 호출
        4. 대시보드 이동
```

---

## 3. API별 FE 사용법

### 입문자 플로우 (`/intro/*`)

#### `POST /api/v1/intro/sessions`
```ts
// 입문자 진입 시 1회 호출. 인증 헤더 불필요.
const { sessionToken, expiresAt } = await post('/api/v1/intro/sessions')
localStorage.setItem('cific_session_token', sessionToken)
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
// 자가진단 기반 진단 문제 10개 조회. answerIndex 미포함.
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

---

## 5. 에러 코드 처리

| 코드 | HTTP | FE 처리 |
|---|---|---|
| `UNAUTHORIZED` | 401 | 로그인 페이지로 리다이렉트 |
| `SESSION_TOKEN_REQUIRED` | 400 | X-Session-Token 헤더 누락 — 세션 재발급 유도 |
| `INVALID_SESSION` | 401 | 존재하지 않는 세션 — 재발급 유도 |
| `SESSION_EXPIRED` | 401 | 세션 만료 → 재발급 또는 회원가입 유도 |
| `SESSION_ALREADY_MERGED` | 409 | 무시 (이미 병합됨) |
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

## 7. 개발 환경

| 항목 | 값 |
|---|---|
| BE 로컬 베이스 URL | `http://localhost:8000` |
| API prefix | `/api/v1` |
| Swagger UI | `http://localhost:8000/docs` |
