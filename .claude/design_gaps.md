# 시안(index_cific.html) vs 현재 백엔드 상이점

> 기준 파일: `design/index_cific.html`
> 기능 구현 시 이 문서를 참고해 누락 없이 반영한다.
> 구현 완료 항목은 ~~취소선~~ 처리한다.

---

## 탭별 상이점

### 홈 탭

| 항목 | 상이점 | 구현 위치 |
|---|---|---|
| 말문제 카드 진입 | `GET /questions?questionType=VERBAL` 필터 미구현 | `app/api/v1/questions/router.py` |
| 전범위 기출 카드 진입 | `GET /questions?isAiGenerated=false` 필터 미구현 (기출=CALCULATION+isAiGenerated=false) | `app/api/v1/questions/router.py` |

---

### 단원학습 탭

#### 과목 카드 — "120문제 · 과목 문제 수"

- 시안: 각 과목 카드에 해당 과목의 총 문제 수 표시 (예: "120문제")
- 현재: `GET /subjects`는 `{ id, subjectName }` 만 반환
- **필요한 변경:**
  - `SubjectResponse`에 `questionCount: int` 추가
  - `SubjectService.list_subjects()`에서 과목별 APPROVED 문제 수 집계
  - `app/repository/subject.py`에 문제 수 집계 쿼리 추가

#### 내 학습 전략 카드

- 시안: 단원학습 상단에 "핵심 개념 우선 공략" 카드 + "전략 수정" 버튼
  - 전략 항목: 반드시 맞힐 영역 / 보완 영역 / 반복 회독 방식
- 현재: DB에 전략 데이터 저장 구조 없음
- **필요한 변경:**
  - USER 테이블에 `studyStrategy` JSON 컬럼 추가 (또는 별도 STRATEGY 테이블)
    - 예: `{ "mustWin": ["재무회계"], "supplement": ["세법"], "mode": "반복 회독" }`
  - `PATCH /users/me` 또는 `POST /users/me/strategy` API 추가
  - `GET /users/me` 응답에 strategy 포함

---

### 오답노트 탭

#### WRONGNOTE ORM 누락 컬럼

- 시안: 카드에 날짜 표시 (08.20), 즐겨찾기 버튼
- 현재 `WRONGNOTE` 테이블에 아래 컬럼 없음:

| 누락 컬럼 | 타입 | 용도 |
|---|---|---|
| `isFavorite` | Boolean, default=False | 즐겨찾기 여부 |
| `createdAt` | DateTime(timezone) | 오답 날짜 표시 |

- **필요한 변경:**
  - `app/models/orm.py` WRONGNOTE에 두 컬럼 추가
  - Alembic 마이그레이션 생성·적용
  - `WrongnoteResponse` 스키마 반영

#### 오답 N회 배지

- 시안: "오답 3회" 배지 (같은 문제를 틀린 누적 횟수)
- 현재: WRONGNOTE에 횟수 컬럼 없음
- **필요한 변경:**
  - `WRONGNOTE`에 `wrongCount` (Integer, default=1) 컬럼 추가 — 같은 questionId로 재오답 시 +1
  - 또는 `ATTEMPT` 기준으로 런타임 집계 (쿼리 복잡도 고려)
  - 구현 시 결정 필요

#### 오답노트 목록 API 없음

- 시안: 오답노트 탭 자체가 목록 화면
- 현재: `GET /wrongnotes` 미존재
- **필요한 변경:**
  - `app/api/v1/wrongnotes/router.py` 생성
  - 쿼리 파라미터: `subjectId` (과목 필터), `isFavorite` (즐겨찾기 필터), `q` (키워드 검색)
  - 응답: `WrongnoteDetailResponse` (문제 stem, 정답, 해설, 과목·개념명 포함)

#### 오답노트 수정 API 없음

- 시안: 코멘트 저장, 즐겨찾기 토글
- 현재: `PATCH /wrongnotes/{id}` 미존재
- **필요한 변경:**
  - `PATCH /wrongnotes/{id}` — `userMemo`, `isFavorite` 수정

---

### 마이프로필 탭

#### 학습 누적일

- 시안: "CPA 1차 · 학습 86일" (가입일~오늘 기준 누적일)
- 현재: `UserResponse`에 미포함
- **필요한 변경:**
  - `GET /users/me` 또는 `GET /home` 응답에 `studyDays: int` 추가
  - 계산: `(today - user.createdAt.date()).days`

#### 최근 정답률

- 시안: 프로필 카드에 "최근 정답률 75%" 표시
- 현재: 계산 로직·API 없음
- **필요한 변경:**
  - `GET /home` 또는 `GET /users/me` 응답에 `recentAccuracy: float` 추가
  - 계산: 최근 N개(예: 50개) ATTEMPT 중 isCorrect 비율

#### 진단분석 시트

- 시안: 과목별 정답률 바 + "잠재적 약점 발견" (반복 실수 패턴)
- 현재: API 없음
- **필요한 변경:**
  - `GET /users/me/analytics` 신규 API
  - 응답: `{ subjectStats: [{ subjectId, subjectName, accuracy }], weakConcepts: [...] }`
  - weakConcepts: MASTERY.score 낮은 개념 목록

#### 전략 수정 시트

- 시안: 반드시 맞힐 영역 / 보완 영역 / 반복 회독 설정 저장
- 현재: DB 저장 구조 없음
- **필요한 변경:** (단원학습 탭 전략 카드와 동일)
  - USER.studyStrategy JSON 컬럼 또는 별도 테이블

---

## 구현 우선순위 제안

| 우선순위 | 항목 | 이유 |
|---|---|---|
| 1 | WRONGNOTE 누락 컬럼 추가 (isFavorite, createdAt, wrongCount) | ORM 변경이므로 API보다 선행 |
| 2 | `GET /wrongnotes` + `PATCH /wrongnotes/{id}` | 오답노트 탭 전체가 이걸로 작동 |
| 3 | `GET /questions?questionType=` 필터 | 홈 말문제·기출 카드 연동 |
| 4 | `GET /subjects` 문제 수 포함 | 단원학습 탭 과목 카드 |
| 5 | `GET /users/me/analytics` | 마이프로필 진단분석 |
| 6 | studyStrategy 저장 구조 | 전략 수정 기능 |
