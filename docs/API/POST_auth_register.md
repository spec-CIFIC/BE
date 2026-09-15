# 회원가입 (Supabase Auth 연동)

HTTP 메서드: POST
HTTP 상태코드: 201 Created, 400 Bad Request, 401 Unauthorized, 409 Conflict, 500 Internal Server Error
URL Path: /api/v1/auth/register
버전: V1
분류: Auth
액세스 토큰 필요: O (Supabase Auth 발급 토큰)

# Request

## Headers

- `Content-Type: application/json`
- `Accept: application/json`
- `Authorization: Bearer {supabaseAccessToken}`

## Body

```json
{
  "subjectId": 1
}
```

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| subjectId | integer | O | 선택한 과목 ID |

# Response

## 201 Created

```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "홍길동",
  "subjectId": 1,
  "provider": "LOCAL",
  "examName": null,
  "examDate": null,
  "streakCount": 0,
  "createdAt": "2025-07-14T09:00:00",
  "updatedAt": "2025-07-14T09:00:00"
}
```

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

```json
{
  "code": "EXPIRED_TOKEN",
  "message": "토큰이 만료되었습니다."
}
```

```json
{
  "code": "INVALID_TOKEN",
  "message": "유효하지 않은 토큰입니다."
}
```

## 409 Conflict

```json
{
  "code": "EMAIL_ALREADY_EXISTS",
  "message": "이미 사용 중인 이메일입니다."
}
```

## 500 Internal Server Error

```json
{
  "code": "INTERNAL_SERVER_ERROR",
  "message": "서버 내부 오류가 발생했습니다."
}
```
