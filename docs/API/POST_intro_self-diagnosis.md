# 자가 진단 약점 제출

HTTP 메서드: POST
HTTP 상태코드: 204 No Content, 400 Bad Request, 401 Unauthorized, 500 Internal Server Error
URL Path: /api/v1/intro/self-diagnosis
버전: V1
분류: Intro
액세스 토큰 필요: X (세션 토큰 필요)

> 사용자가 스스로 약하다고 생각하는 개념 ID를 제출한다. 이후 진단 문제(`GET /intro/questions`)가 이 정보를 기반으로 구성된다.

# Request

## Headers

- `Content-Type: application/json`
- `Accept: application/json`
- `X-Session-Token: {sessionToken}`

## Body

```json
{
  "weakConceptIds": [1, 3, 5]
}
```

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| weakConceptIds | integer[] | O | 약하다고 선택한 개념 ID 목록 |

# Response

## 204 No Content

응답 바디 없음.

## 400 Bad Request

```json
{
  "code": "SESSION_TOKEN_REQUIRED",
  "message": "세션 토큰이 필요합니다."
}
```

```json
{
  "code": "INVALID_REQUEST",
  "message": "요청 값이 올바르지 않습니다."
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
