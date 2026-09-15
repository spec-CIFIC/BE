# 학습 계획 등록

HTTP 메서드: POST
HTTP 상태코드: 201 Created, 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Server Error
URL Path: /api/v1/study-plan
버전: V1
분류: StudyPlan
액세스 토큰 필요: O

> 집중적으로 학습할 개념을 일괄 등록한다. 이미 등록된 개념은 무시하고, 신규 개념만 추가된다.  
> 등록된 개념은 복습 큐, 오답노트 등에서 우선 노출된다.

# Request

## Headers

- `Content-Type: application/json`
- `Accept: application/json`
- `Authorization: Bearer {accessToken}`

## Body

```json
{
  "conceptIds": [1, 3, 5]
}
```

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| conceptIds | integer[] | O | 등록할 개념 ID 목록 |

# Response

## 201 Created

```json
{
  "items": [
    {
      "conceptId": 1,
      "conceptName": "감가상각",
      "createdAt": "2025-07-14T09:00:00"
    },
    {
      "conceptId": 3,
      "conceptName": "현재가치",
      "createdAt": "2025-07-12T09:00:00"
    },
    {
      "conceptId": 5,
      "conceptName": "리스회계",
      "createdAt": "2025-07-14T09:00:00"
    }
  ]
}
```

> 기존에 등록된 항목을 포함한 전체 학습 계획 목록을 반환한다.

## 400 Bad Request

```json
{
  "code": "INVALID_REQUEST",
  "message": "요청 값이 올바르지 않습니다."
}
```

## 401 Unauthorized

```json
{
  "code": "UNAUTHORIZED",
  "message": "인증이 필요합니다."
}
```

## 404 Not Found

```json
{
  "code": "STUDY_PLAN_CONCEPT_NOT_FOUND",
  "message": "존재하지 않는 개념이 포함되어 있습니다."
}
```

## 500 Internal Server Error

```json
{
  "code": "INTERNAL_SERVER_ERROR",
  "message": "서버 내부 오류가 발생했습니다."
}
```
