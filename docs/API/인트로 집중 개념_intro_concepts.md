# 진단 개념 목록 조회

HTTP 메서드: GET
HTTP 상태코드: 200 OK, 400 Bad Request, 401 Unauthorized, 500 Internal Server Error
URL Path: /api/v1/intro/concepts
버전: V1
분류: Intro
액세스 토큰 필요: X (세션 토큰 필요)

> 과목 선택(`POST /intro/subject`) 완료 후 호출. 해당 과목의 개념 목록을 반환하며, 사용자가 약점 개념을 선택하는 데 사용한다.

# Request

## Headers

- `Accept: application/json`
- `X-Session-Token: {sessionToken}`

# Response

## 200 OK

```json
[
  { "id": 1, "conceptName": "감가상각" },
  { "id": 2, "conceptName": "원가계산" },
  { "id": 3, "conceptName": "현재가치" }
]
```

## 400 Bad Request

```json
{
  "code": "SESSION_TOKEN_REQUIRED",
  "message": "세션 토큰이 필요합니다."
}
```

```json
{
  "code": "SUBJECT_REQUIRED",
  "message": "과목을 먼저 선택해주세요."
}
```

## 401 Unauthorized

```json
{
  "code": "INVALID_SESSION",
  "message": "유효하지 않은 세션입니다."
}
```

```json
{
  "code": "SESSION_EXPIRED",
  "message": "세션이 만료되었습니다."
}
```

## 500 Internal Server Error

```json
{
  "code": "INTERNAL_SERVER_ERROR",
  "message": "서버 내부 오류가 발생했습니다."
}
```
