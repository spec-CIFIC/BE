# 내 프로필 수정

HTTP 메서드: PATCH
HTTP 상태코드: 200 OK, 400 Bad Request, 401 Unauthorized, 500 Internal Server Error
URL Path: /api/v1/users/me
버전: V1
분류: User
액세스 토큰 필요: O

# Request

## Headers

- `Content-Type: application/json`
- `Accept: application/json`
- `Authorization: Bearer {accessToken}`

## Body

모든 필드는 선택 사항이며, 전달된 필드만 업데이트된다.

```json
{
  "name": "홍길동",
  "subjectId": 2,
  "examName": "CPA 1차",
  "examDate": "2025-11-01"
}
```

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| name | string | X | 사용자 이름 |
| subjectId | integer | X | 시험 과목 ID |
| examName | string | X | 목표 시험명 |
| examDate | string (date) | X | 시험일 (YYYY-MM-DD) |

# Response

## 200 OK

```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "홍길동",
  "subjectId": 2,
  "provider": "LOCAL",
  "examName": "CPA 1차",
  "examDate": "2025-11-01",
  "streakCount": 5,
  "createdAt": "2025-07-01T12:00:00",
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

## 500 Internal Server Error

```json
{
  "code": "INTERNAL_SERVER_ERROR",
  "message": "서버 내부 오류가 발생했습니다."
}
```
