# 홈화면 데이터 조회

HTTP 메서드: GET
HTTP 상태코드: 200 OK, 401 Unauthorized, 500 Internal Server Error
URL Path: /api/v1/home
버전: V1
분류: Home
액세스 토큰 필요: O

# Request

## Headers

- `Authorization: Bearer {accessToken}`
- `Accept: application/json`

# Response

## 200 OK

```json
{
  "user": {
    "name": "홍길동",
    "streakCount": 5
  },
  "examGoal": {
    "examName": "CPA 1차",
    "examDate": "2025-11-01",
    "dDay": 110
  },
  "reviewQueue": {
    "reviewConceptCount": 3,
    "wrongNoteCount": 7
  },
  "dailyStrategy": "오늘은 감가상각 개념을 집중적으로 복습해보세요.",
  "hasStudyPlan": true
}
```

| 필드 | 타입 | 설명 |
|---|---|---|
| user.name | string | 유저 이름 |
| user.streakCount | integer | 연속 학습일 수 |
| examGoal | object \| null | 시험 목표 (설정하지 않은 경우 null) |
| examGoal.dDay | integer | 시험까지 남은 일수 |
| reviewQueue.reviewConceptCount | integer | 에빙하우스 기준 오늘 복습 예정 개념 수 |
| reviewQueue.wrongNoteCount | integer | 오늘 복습 예정 오답노트 수 |
| dailyStrategy | string | AI 생성 오늘의 학습 전략 문구 |
| hasStudyPlan | boolean | 학습 계획(STUDY_PLAN) 등록 여부 |

## 401 Unauthorized

```json
{
  "code": "UNAUTHORIZED",
  "message": "인증이 필요합니다."
}
```

## 500 Internal Server Error

```json
{
  "code": "INTERNAL_SERVER_ERROR",
  "message": "서버 내부 오류가 발생했습니다."
}
```
