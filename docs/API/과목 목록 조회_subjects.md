# 과목 목록 조회

HTTP 메서드: GET
HTTP 상태코드: 200 OK, 500 Internal Server Error
URL Path: /api/v1/subjects
버전: V1
분류: Subject
액세스 토큰 필요: X

# Request

## Headers

- `Accept: application/json`

# Response

## 200 OK

```json
[
  { "id": 1, "subjectName": "재무회계" },
  { "id": 2, "subjectName": "세법" },
  { "id": 3, "subjectName": "원가관리회계" }
]
```

## 500 Internal Server Error

```json
{
  "code": "INTERNAL_SERVER_ERROR",
  "message": "서버 내부 오류가 발생했습니다."
}
```
