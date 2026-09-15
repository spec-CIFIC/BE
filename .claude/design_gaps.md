# 시안(index_cific.html) vs 현재 백엔드 상이점

> 기준 파일: `design/index_cific.html`
> 기능 구현 시 이 문서를 참고해 누락 없이 반영한다.
> 구현 완료 항목은 ~~취소선~~ 처리한다.

---

## 탭별 상이점

### 홈 탭

| 항목 | 상이점 | 구현 위치 |
|---|---|---|
| ~~말문제 카드 진입~~ | ~~`GET /questions?filter=verbal` 구현됨~~ | `app/api/v1/questions/router.py` |
| ~~전범위 기출 카드 진입~~ | ~~`GET /questions?filter=past_exam` 구현됨~~ | `app/api/v1/questions/router.py` |

---

### 단원학습 탭

#### ~~과목 카드 — "120문제 · 과목 문제 수"~~

- ~~`GET /subjects` 응답에 `questionCount` 포함. APPROVED 문제 수 집계.~~

#### 내 학습 전략 카드

- 시안: 단원학습 상단에 "핵심 개념 우선 공략" 카드 + "전략 수정" 버튼
  - 전략 항목: 반드시 맞힐 영역 / 보완 영역 / 반복 회독 방식
- 현재: DB에 전략 데이터 저장 구조 없음
- **v3 이월**

---

### 오답노트 탭

#### ~~WRONGNOTE ORM 누락 컬럼~~

- ~~`isFavorited`, `wrongCount`, `updatedAt` 모두 ORM에 추가됨~~

#### ~~오답노트 목록 API~~

- ~~`GET /wrongnotes` 구현됨. `q`, `subjectId`, `isFavorited` 필터 지원~~

#### ~~오답노트 수정 API~~

- ~~`PATCH /wrongnotes/{id}` (userMemo), `PATCH /wrongnotes/{id}/favorite` 구현됨~~

---

### 마이프로필 탭

#### ~~학습 누적일~~

- ~~`GET /users/me` 응답에 `studyDays` 포함. `(today - createdAt.date()).days` 계산~~

#### ~~최근 정답률 → 주간 풀이 수로 대체~~

- ~~`weeklyAttemptCount` (최근 7일 풀이 수)로 대체 결정. `GET /users/me` 응답에 포함~~

#### 진단분석 시트

- 시안: 과목별 정답률 바 + "잠재적 약점 발견" (반복 실수 패턴)
- 현재: API 없음
- **v3 이월** — `GET /users/me/analytics`

#### 전략 수정 시트

- 시안: 반드시 맞힐 영역 / 보완 영역 / 반복 회독 설정 저장
- 현재: DB 저장 구조 없음
- **v3 이월**

---

## 구현 우선순위 제안

| 우선순위 | 항목 | 상태 |
|---|---|---|
| 1 | WRONGNOTE 컬럼 (isFavorited, wrongCount) | ✅ 완료 |
| 2 | `GET /wrongnotes` + `PATCH /wrongnotes/{id}` | ✅ 완료 |
| 3 | `GET /questions?filter=` 필터 | ✅ 완료 |
| 4 | `GET /subjects` questionCount | ✅ 완료 |
| 5 | `studyDays`, `weeklyAttemptCount` in `GET /users/me` | ✅ 완료 |
| 6 | `GET /users/me/analytics` | v3 이월 |
| 7 | studyStrategy 저장 구조 | v3 이월 |
