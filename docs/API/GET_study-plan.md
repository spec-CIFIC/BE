# 학습 계획 목록 조회

HTTP 메서드: GET
HTTP 상태코드: 200 OK, 401 Unauthorized, 500 Internal Server Error
URL Path: /api/v1/study-plan
버전: V1
분류: StudyPlan
액세스 토큰 필요: O

# Request

## Headers

- `Authorization: Bearer {accessToken}`
- `Accept: application/json`

# Response

## 200 OK

```json
{
  "items": [
    {
      "conceptId": 1,
      "conceptName": "감가상각",
      "createdAt": "2025-07-10T09:00:00"
    },
    {
      "conceptId": 3,
      "conceptName": "현재가치",
      "createdAt": "2025-07-12T09:00:00"
    }
  ]
}
```

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
