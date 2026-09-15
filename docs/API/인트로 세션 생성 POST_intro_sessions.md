# 익명 세션 생성

HTTP 메서드: POST
HTTP 상태코드: 201 Created, 500 Internal Server Error
URL Path: /api/v1/intro/sessions
버전: V1
분류: Intro
액세스 토큰 필요: X

# Request

## Headers

- `Accept: application/json`

# Response

## 201 Created

```json
{
  "sessionToken": "abc123xyz...",
  "expiresAt": "2025-07-21T09:00:00"
}
```

| 필드 | 타입 | 설명 |
|---|---|---|
| sessionToken | string | 이후 intro 플로우 요청에 `X-Session-Token` 헤더로 사용 |
| expiresAt | datetime | 세션 만료 시각 |

## 500 Internal Server Error

```json
{
  "code": "INTERNAL_SERVER_ERROR",
  "message": "서버 내부 오류가 발생했습니다."
}
```
