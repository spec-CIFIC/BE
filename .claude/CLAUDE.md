# CIFIC — Backend (specIFIC)

자격시험 AI 학습 플랫폼. 인강·교재로 배운 내용을 AI가 약점만 골라 무한히 문제로 뽑아주고, 자동으로 오답노트까지 만들어주는 **복습·연습 레이어**. 첫 타깃 시험: **CPA(공인회계사)**.

---

## 현재 진행 단계

> **현재: v0 — BE·FE 스켈레톤**

@.claude/plans/v0_skeleton.md ← 진행 중
@.claude/plans/v1_ui.md
@.claude/plans/v2_reliability.md
@.claude/plans/v3_flywheel.md

> 시안(design/index_cific.html)과 현재 백엔드의 상이점 목록 → @.claude/design_gaps.md

---

## 프로젝트 개요

### 핵심 포지셔닝
기존 인강/교재의 **대체재가 아닌 보완재**. 약점 진단 → 맞춤 문제 생성 → 자동 오답노트의 순환 구조.

### 왜 CPA/회계인가
회계·세무의 계산 문제(감가상각·원가계산·세액계산)는 답이 결정론적으로 딱 떨어진다. 즉 **AI가 문제를 잘 만들었는지 코드로 채점**할 수 있다. 생성은 못 믿어도 검증(채점)은 믿을 수 있는 드문 도메인.

### 시스템 흐름
```
지식베이스 → 문제 생성 엔진 → 검증 파이프라인 → 검증된 문제 뱅크
                   ▲                                       │
                   │                                       ▼
            (약점 기반 재생성) ← 약점 진단·맞춤 추천 ← 학습자 이용
```

---

## 기술 스택

| 레이어 | 선택 | 상태 |
|---|---|---|
| 백엔드 | Python + FastAPI | **확정** |
| ORM / 마이그레이션 | SQLAlchemy + Alembic | **확정** |
| DB | PostgreSQL + pgvector | **확정** |
| 프론트엔드 | Next.js + TypeScript | **확정** |
| UI | Tailwind CSS + shadcn/ui | **확정** |
| 인증 | Supabase Auth | 권장 (변경 가능) |
| LLM | Anthropic Claude / OpenAI GPT API | 권장 (변경 가능) |
| 임베딩 (RAG) | BGE-M3 등 다국어 임베딩 | 권장 (변경 가능) |
| 배포 | AWS Amplify(FE) + AWS EC2(BE) + AWS RDS(DB) | 권장 (변경 가능) |

### 아키텍처 원칙
- 지식은 **RAG로 주입** (파인튜닝 아님). 법·세무는 자주 바뀌고 근거 추적이 필요하므로 파인튜닝 부적합.
- 문제 생성은 **실시간이 아니라 배치**로 생성·검증 후 뱅크에 적재, 서빙은 뱅크에서 즉시.
- RAG 오케스트레이션은 파이프라인이 단순하면(검색→프롬프트 조립→생성) LangChain/LlamaIndex 없이 직접 구현이 디버깅에 유리.
- pgvector로 벡터 검색을 처리해 별도 벡터 DB 없이 인프라 단순화.

---

## 검증 파이프라인 (5단계)

문제 하나가 생성되면 아래 5개 게이트를 통과한다. 통과/탈락 이분법이 아닌 **신뢰도 점수로 분류**.

| 단계 | 검증 내용 | 방식 |
|---|---|---|
| 1. 구조 검증 | 선지 개수, 정답 존재, 해설 누락 등 형식 | 순수 코드 |
| 2. 계산 검증 **(핵심)** | 생성된 풀이 코드를 실행 → 주장한 정답과 대조 | 코드 실행 (샌드박스) |
| 3. 교차 검증 | 정답 숨기고 다른 모델이 풀게 함 → 답 일치 여부 | LLM |
| 4. 근거 대조 | 해설의 주장이 지식베이스 조문·기준과 일치하는지 | RAG + entailment |
| 5. 기출 유사도 | 임베딩 유사도로 기출과 너무 비슷하면 폐기 (저작권) | 임베딩 |

**신뢰도 라우팅:**
- 高신뢰 → 자동 승인 (바로 출제)
- 中신뢰 → 사람 검수
- 低신뢰 → 폐기 / 재생성

---

## DB 스키마 (ORM)

파일: `app/models/orm.py`

| 테이블 | 역할 |
|---|---|
| `SUBJECT` | 과목 (예: 재무회계) |
| `CONCEPT` | 개념 (예: 감가상각) |
| `QUESTIONS` | 검증된 문제 뱅크. `choices`는 JSON, `stem`은 Text |
| `USER` | 회원. `password`는 소셜 로그인 시 null, `provider`는 LOCAL/GOOGLE/KAKAO |
| `ANON_SESSION` | 익명 세션. 로그인 시 `mergedUserId`로 병합 |
| `ATTEMPT` | 풀이 기록. `userId`/`anonSessionId` 중 하나만 채워짐 |
| `MASTERY` | 개념별 숙련도 점수 (0.0~1.0) + sampleSize. attempt 제출마다 EMA(α=0.3)로 갱신 |
| `WRONGNOTE` | 오답노트. `mistakeType`(AI 판정), `reviewDueAt`(에빙하우스 간격 반복) |
| `STUDY_PLAN` | 사용자가 집중하기로 선택한 concept 목록. (userId, conceptId, createdAt) |

`schemas.py`: HTTP 요청/응답용 Pydantic 모델 (외부용)
`orm.py`: DB 테이블 구조 SQLAlchemy 모델 (내부용) — 둘은 역할이 다르므로 분리 유지.

### STUDY_PLAN 설계 의도

`STUDY_PLAN`은 사용자가 집중적으로 파고들 concept을 직접 선택해 저장하는 테이블이다.
숙련도(MASTERY)는 시스템이 측정한 값이고, STUDY_PLAN은 사용자의 의도/전략이므로 분리한다.

**STUDY_PLAN에 등록된 concept은 앱 전반에서 우선 노출된다:**

| 화면 | 적용 방식 |
|---|---|
| 오늘의 복습 큐 (`GET /home`) | `reviewConceptCount` 집계 및 `/review/concepts` 응답에서 STUDY_PLAN concept 먼저 정렬 |
| 단원 학습 | 개념 목록에서 STUDY_PLAN concept을 시각적으로 강조 (FE 처리) |
| 오답노트 (`GET /review/wrongnotes`) | STUDY_PLAN에 속한 concept의 오답노트를 먼저 정렬 |

### 복습 진입 구조 (홈 "추천 복습" — 에빙하우스 기반)

홈 "추천 복습" 섹션의 두 카드가 각각 다른 스트림에 연결된다.

- **왼쪽 "다시 풀어볼 문제"** → `GET /review/concepts`. **개념 복습을 에빙하우스로 스케줄**한다.
  `MASTERY.nextReviewAt`(≤ now 또는 null)인 개념을 노출하며, attempt마다 정답이면 간격을 늘리고
  (`reviewStage` +1) 오답이면 리셋한다. 간격: `[1,3,7,14,30]`일. 홈 `reviewConceptCount`도 이 기준.
- **오른쪽 "다시 볼 오답"** → `GET /review/wrongnotes`. `WRONGNOTE.reviewDueAt`(≤ now) 기반(별도 에빙하우스).

두 목록 모두 STUDY_PLAN concept을 먼저 정렬하고 각 항목에 `isStudyPlan`을 담는다.
concept 선택 시 `GET /review/wrongnotes?conceptId=`로 드릴다운한다.

### 오답노트 복습 UX 계약 (FE 오버레이)

오답노트 상세는 **페이지 이동이 아니라 기존 화면 위 오버레이 모달**로 뜬다(우상단 X로 닫기).

- 문제(stem·choices)를 먼저 보여주고, **"해설 및 정답 보기" 토글**로 `answerIndex`·`explanation`을 접었다 폈다 한다.
- **"코멘트 추가" = `WRONGNOTE.userMemo`** → `PATCH /review/wrongnotes/{id}`로 저장한다.
- `GET /review/wrongnotes` 응답이 문제 본문·정답·해설·userMemo까지 포함하므로 오버레이는 이 데이터를 바로 쓴다.

**이 오버레이 UI 컴포넌트는 하단바 "오답노트" 탭과 공유하되, 데이터 API는 다르다.**
복습 진입(`/review/wrongnotes`)은 복습 예정분(`reviewDueAt ≤ now`)만 내려주고, 하단바 "오답노트" 탭은
전체 오답노트를 훑어보는 별도 화면이라 **전체 목록용 엔드포인트(예: `GET /wrongnotes`)가 따로 필요**하다.
(이 전체 목록 API는 해당 탭 기능 개발 시점에 추가 — 지금은 미구현)

---

## 프로젝트 구조

```
BE/
├── app/
│   ├── api/          # FastAPI 라우터
│   ├── core/         # 설정, 공통 유틸
│   ├── db/
│   │   └── database.py   # DB 연결, Base
│   ├── models/
│   │   ├── domain.py     # 도메인 모델
│   │   ├── orm.py        # SQLAlchemy ORM
│   │   └── schemas.py    # Pydantic 스키마
│   ├── processors/   # 문제 생성·검증 파이프라인
│   ├── services/     # 비즈니스 로직
│   ├── validators/   # 검증 게이트 구현
│   └── main.py       # FastAPI 앱 진입점
├── tests/
├── requirements.txt
├── requirements-dev.txt
└── environment.yml
```

---

## 로드맵

| 버전 | 범위 | 목표 |
|---|---|---|
| **v0** | 회계 1유형 + 검증 1·2단계 | 생성→코드실행→대조 루프 데모 |
| **v1** | 검증 3·5단계 + 문제풀이 UI | 실제로 풀 수 있는 형태 |
| **v2** | 검증 4단계 + 신뢰도 라우팅 + eval/골드셋 | 자동 승인율 % 측정 가능 |
| **v3** | 약점진단·대시보드 + 오답노트 + 프리랜서 검수 | 플라이휠 가동, 소규모 베타 |
| 이후 | CPA 전과목 → 세무사 확장 | 콘텐츠팩 추가 |

---

## 코딩 규칙

코드 작성 시 `.flake8` 규칙을 준수한다. 파일 수정 후 `flake8 app/`으로 확인.

---

## 에러코드 관리 원칙

`app/exception/constant/` 하위 에러코드는 **기능 개발 시점에 해당 도메인 파일을 추가**한다. 명세 없이 미리 전부 정의하지 않는다.

- 현재 정의된 것은 인프라 레벨(인증·공통·서버에러)만 — 어떤 기능이 와도 필요한 것들
- 새 도메인 API 개발 시 `XxxErrorCode.py` 파일을 그때 추가

예시: 유저 API 개발 → `user.py` 추가 / 과목 API → `subject.py` 추가

---

## Service / Repository 메서드 주석 원칙

`app/services/` 및 `app/repository/` 하위 **모든 메서드**에는 다음을 주석으로 명시한다.

- **어떤 엔드포인트(또는 시나리오)에서 호출되는지**
- **파라미터가 여러 경우로 분기될 때 각 경우의 동작**

```python
# 예시 — service
async def list_questions(...):
    # GET /questions — 문제 목록 조회
    # source: past_exam 지정 시 isAiGenerated=false(기출) 문제만 반환

# 예시 — repository
async def find_approved(...):
    # GET /questions 목록 조회 — 과목·개념·유형·출처 필터 + 페이지네이션
```

## Repository 관리 원칙

`app/repository/` 하위 쿼리는 **기능 개발 시점에 함께 추가·수정**한다. 미래 기능을 위한 쿼리를 미리 작성하지 않는다.

- 새 API가 추가될 때 필요한 쿼리가 없으면 해당 repository에 메서드를 추가한다
- 기존 쿼리로 커버 가능하면 재사용하고, 변경이 필요하면 그때 수정한다

예시: 오답노트 API 개발 → `wrongnote.py` 추가 / 숙련도 조회 → `mastery.py` 추가

---

## FE 연동 문서

BE API가 추가·변경될 때 `docs/fe-integration.md`를 함께 업데이트한다.

- 인증 헤더 규칙, localStorage 키, 에러 코드 처리 등 Swagger에 없는 계약을 다룬다
- 새 API 추가 시: 엔드포인트 사용법·에러 처리를 해당 문서에 반영

---

## 오픈 이슈

- LLM: 시작 API 벤더 확정 (Anthropic vs OpenAI), 임베딩 모델 확정
- 계산 검증 샌드박스 실행 환경 선정
- 첫 진입 과목: 재무회계 vs 세법
- 오픈소스 자체 호스팅 전환 시점 기준 (트래픽/비용 임계값)

---

@.claude/rules/git.md
@.claude/rules/notion.md
