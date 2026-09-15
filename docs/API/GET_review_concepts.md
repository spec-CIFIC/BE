# 에빙하우스 복습 예정 개념 목록

HTTP 메서드: GET
HTTP 상태코드: 200 OK, 401 Unauthorized, 500 Internal Server Error
URL Path: /api/v1/review/concepts
버전: V1
분류: Review
액세스 토큰 필요: O

> `MASTERY.nextReviewAt ≤ now` 또는 `nextReviewAt IS NULL`인 개념을 반환한다.  
> STUDY_PLAN에 등록된 개념이 먼저 정렬되고, 이후 숙련도(score) 낮은 순으로 정렬된다.  
> 홈화면 `reviewConceptCount`와 같은 기준이다.

# Request

## Headers

- `Authorization: Bearer {accessToken}`
- `Accept: application/json`

# Response

## 200 OK

```json
[
  {
    "conceptId": 3,
    "conceptName": "현재가치",
    "score": 0.3,
    "nextReviewAt": null,
    "isStudyPlan": true
  },
  {
    "conceptId": 1,
    "conceptName": "감가상각",
    "score": 0.5,
    "nextReviewAt": "2025-07-14T00:00:00",
    "isStudyPlan": false
  }
]
```

| 필드 | 타입 | 설명 |
|---|---|---|
| conceptId | integer | 개념 ID |
| conceptName | string | 개념명 |
| score | float | 현재 숙련도 (0.0~1.0) |
| nextReviewAt | datetime \| null | 다음 복습 예정 시각 (null이면 미복습) |
| isStudyPlan | boolean | 학습 계획 등록 여부 |

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
