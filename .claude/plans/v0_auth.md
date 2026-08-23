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

---

## Supabase 환경 설정 (개발 중 필수 인지 사항)

> 이 문서는 BE/FE 양쪽 `.claude/plans/`에 동일하게 유지한다.

### Confirm email = OFF (현재 개발 설정)

- **상태**: Supabase Authentication → Sign In / Providers → Email → **"Confirm email" OFF**
- **이유**: Confirm email이 켜져 있으면 `supabase.auth.signUp` 직후 `session`이 `null`로 반환된다.
  그러면 FE가 `accessToken`을 못 받아 `register`/`merge`를 못 하고 회원가입이 대시보드로 넘어가지 않는다.
  (증상: "가입은 되었지만 자동 로그인되지 않았습니다" 안내 노출 — `app/(auth)/signup.tsx`)
- **끄면**: signUp 즉시 session 발급 → `register` → `merge` → 대시보드까지 자동 진행.

### 운영 전환 시 주의

- 프로덕션에서는 Confirm email을 **다시 켜는 것**을 검토한다(스팸/도용 방지).
- 켤 경우 FE는 "확인 메일을 확인해주세요" 안내 후, 메일 인증 완료 → 로그인 → `merge` 흐름으로 설계해야 한다.
  (현재 login 경로는 `lib/auth/link.ts`의 `linkAnonAccount`로 USER 없으면 register 선행 후 merge까지 처리함)

### 테스트 팁

- 이미 가입 시도한 이메일은 `auth.users`에 (미확인 상태로) 남는다. 같은 이메일 재가입은 막히므로,
  **Authentication → Users에서 삭제** 후 재시도하거나 다른 이메일을 쓴다.

---

## 후속 작업 (백로그)

> 지금 단계에서는 구현하지 않고, 명세가 확정되는 시점에 착수한다. (CLAUDE.md YAGNI 원칙)

### 1. 전화번호 SMS 인증
- **현재**: `USER.phone`은 **단순 저장**만 한다 (인증 없음).
- **후속**: 출시 임박 시 Supabase Phone Auth(OTP)로 SMS 인증 추가.
  - SMS provider(Twilio 등) 연동 필요 + **건당 과금** 발생.
  - 인증 완료 여부 표시용 컬럼(`phoneVerifiedAt` 등)은 그때 함께 추가.

### 2. 이메일 중복 처리 견고화 ✅ 완료
- **현재**: 중복은 Supabase Auth(1차) + `USER.email` unique(2차)로 막힌다.
- **개선 완료**: `UserRepository.create`가 `IntegrityError`를 uid/email 충돌로 분기.
  email 충돌 시 500 대신 `EMAIL_ALREADY_EXISTS`(409) 반환 (`UserErrorCode`).
- **안 함**: "가입 전 이메일 중복확인 API"는 enumeration 보안 이슈로 만들지 않는다.

### 3. USER 테이블 필드 확장
> 스키마 변경(마이그레이션) + 각 필드의 **운영 로직**까지 필요해 별도 작업으로 분리한다.

추가 예정 필드 (`app/models/orm.py` USER):

| 필드 | 타입 | 용도 | 함께 필요한 로직 |
|---|---|---|---|
| `status` | varchar(20) | ACTIVE/DORMANT/WITHDRAWN 계정 상태 | 상태 전이 규칙, 휴면 전환 배치, 탈퇴 처리 |
| `deletedAt` | timestamptz null | soft delete (탈퇴) | 조회 시 `deletedAt IS NULL` 필터 전반 반영 |
| `targetExamDate` | date null | CPA 목표 시험일 (D-day) | 프로필 수정 API에 필드 추가, D-day 계산 |
| `lastLoginAt` | timestamptz null | 리텐션 분석 | 로그인/인증 시점 갱신 로직 (`get_from_token` 등) |
| `phone` | varchar(20) null | 전화번호 (단순 저장) | 프로필 수정 API에 필드 추가 (인증은 위 1번 후속) |

- **주의**: 단순 컬럼 추가로 끝나지 않는다. 예) `deletedAt`은 모든 유저 조회 쿼리에 필터가 필요하고,
  `status`/`lastLoginAt`은 상태 전이·갱신 로직이 따라붙는다. 컬럼만 넣고 로직을 빼면 죽은 필드가 된다.
- **진행 순서**: 필드별로 "컬럼 + 해당 로직"을 한 묶음으로 쪼개서 필요한 것부터 착수.
- **`password` 제거 검토**: Supabase Auth와 중복인 사실상 죽은 필드. 참조처 확인 후 별도 마이그레이션으로 제거.
- 스키마 변경 시 `git.md` 절차 준수: orm.py → 마이그레이션 → `MVP_ERD.md`/`SCHEMA_MANAGEMENT.md` 동기화.

### 4. merge — ATTEMPT 실제 이전 (현재 "반쪽" 구현)
- **현재 동작**: `merge_session`(→`AnonSessionRepository.set_merged_user`)은
  `ANON_SESSION.mergedUserId`만 세팅한다. **익명 `ATTEMPT`는 그대로** (`anonSessionId`만 있고 `userId`는 null).
  → 로그인해도 익명 풀이기록이 계정 기록(`userId` 기준 조회)으로 **실제로 붙지 않는다.**
- **원래 계획과 차이**: 이 문서 위 "3. POST /auth/merge" 항목은
  "세션의 ATTEMPT 전체 → `userId` 업데이트, `anonSessionId` null 처리"였으나 구현이 마킹만 하고 이전을 뺐다.
- **왜 지금 안 고치나**: 이 경로가 트리거되는 건 *이미 계정이 있는 사람이 실수로 "처음 이용해요"로
  익명 풀이를 쌓은 뒤 로그인*하는 엣지케이스다. 손실되는 건 그 실수 세션의 익명 attempt 몇 건뿐이라
  우선순위가 낮다. (정상 플로우: 익명 → 신규 회원가입 → merge 는 attempt가 적고 신규라 영향 미미)
- **완성하려면**: `attempt` repo에 이전 메서드 추가
  (`UPDATE ATTEMPT SET "userId"=:uid, "anonSessionId"=NULL WHERE "anonSessionId"=:sid`) →
  `merge_session`에서 `set_merged_user`와 함께 호출. ORM 원칙(attempt는 userId/anonSessionId 중 하나만)과 일치.
