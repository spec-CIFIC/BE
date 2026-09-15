# 현재 로그인 유저 정보 조회

HTTP 메서드: GET
HTTP 상태코드: 200 OK, 401 Unauthorized, 500 Internal Server Error
URL Path: /api/v1/auth/me
버전: V1
분류: Auth
액세스 토큰 필요: O

# Request

## Headers

- `Authorization: Bearer {accessToken}`
- `Accept: application/json`

# Response

## 200 OK

```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "홍길동",
  "subjectId": 1,
  "provider": "LOCAL",
  "examName": "CPA 1차",
  "examDate": "2025-11-01",
  "streakCount": 5,
  "createdAt": "2025-07-01T12:00:00",
  "updatedAt": "2025-07-14T09:00:00"
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

## 500 Internal Server Error

```json
{
  "code": "INTERNAL_SERVER_ERROR",
  "message": "서버 내부 오류가 발생했습니다."
}
```
