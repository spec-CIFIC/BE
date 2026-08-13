# v0 — 인증·인가 플랜

> 근거: 입문자 페이지_설계전략 (Notion)
> 핵심 전략: 첫 화면에서 신규/기존 유저를 분기 → 신규는 익명 세션으로 먼저 경험 후 회원가입 유도

---

## 사용자 플로우

```
첫 화면
  ├── "처음 이용해요" (입문자)
  │     → POST /sessions           익명 세션 발급
  │     → POST /attempts (익명)    진단 테스트 풀이 (anonSessionId로 저장)
  │     → 약점 리포트 확인
  │     → 회원가입 유도
  │     → Supabase Auth 회원가입·로그인
  │     → POST /auth/merge         익명 세션 → 유저 계정 병합
  │     → 대시보드
  │
  └── "기존 회원이에요" (숙련자)
        → Supabase Auth 로그인
        → 대시보드 (학습 로그 기반 약점 추천)
```

---

## 구현할 API

### 1. `POST /sessions` — 익명 세션 발급 (입문자 전용)
- 인증 불필요
- UUID 기반 `sessionToken` 생성 → `ANON_SESSION` DB 저장
- 만료 시간(`expiresAt`): 발급 후 7일
- Response: `{ sessionToken, expiresAt }`

### 2. `POST /attempts` — 익명 풀이 제출 지원
- 기존: 로그인 필수 (`get_current_user`)
- 변경: Bearer 토큰 없으면 `X-Session-Token` 헤더로 익명 세션 조회
- `userId` 또는 `anonSessionId` 중 하나만 저장 (ORM 기존 설계 그대로)
- 만료된 세션이면 `401` 반환

### 3. `POST /auth/merge` — 익명 → 유저 병합 (회원가입 직후 1회)
- 인증 필수 (Supabase JWT)
- Body: `{ sessionToken }`
- 로직:
  1. `sessionToken`으로 `ANON_SESSION` 조회
  2. 해당 세션의 `ATTEMPT` 레코드 전체 → `userId` 업데이트, `anonSessionId` null 처리
  3. `ANON_SESSION.mergedUserId` 세팅
- 이미 병합된 세션이면 `409` 반환
- Response: 병합된 attempt 개수

---

## 새로 생성할 파일

```
app/api/v1/sessions/
├── __init__.py
└── router.py

app/repository/
└── anon_session.py       # ANON_SESSION CRUD

app/services/
└── session.py            # 세션 발급·병합 로직

app/exception/constant/
└── session.py            # SessionErrorCode
```

## 수정할 파일

```
app/api/v1/attempts/router.py   # 익명 세션 지원
app/api/v1/auth/router.py       # POST /auth/merge 추가
app/api/v1/router.py            # sessions 라우터 등록
app/api/deps.py                 # 익명 세션 의존성 추가
```

---

## 에러코드 (`session.py`)

| 코드 | 상태 | 설명 |
|---|---|---|
| `SESSION_NOT_FOUND` | 404 | 세션을 찾을 수 없음 |
| `SESSION_EXPIRED` | 401 | 세션이 만료됨 |
| `SESSION_ALREADY_MERGED` | 409 | 이미 병합된 세션 |

---

## 완료 기준

- [ ] 첫 화면에서 입문자/기존 회원 분기 동작
- [ ] 비로그인 상태로 문제 풀이 제출 가능 (입문자 플로우)
- [ ] 기존 회원은 로그인 후 바로 대시보드 진입
- [ ] 회원가입 후 merge 호출 시 익명 attempt → 유저 계정으로 이전
- [ ] 만료 세션 요청 시 401 반환
- [ ] 이미 병합된 세션 재병합 시 409 반환
