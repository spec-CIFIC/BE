# 풀이 제출

HTTP 메서드: POST
HTTP 상태코드: 201 Created, 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Server Error
URL Path: /api/v1/attempts
버전: V1
분류: Attempt
액세스 토큰 필요: O

> 로그인 유저의 풀이를 제출한다. 제출 시 MASTERY 점수가 EMA(α=0.3)로 갱신되고, 오답일 경우 WRONGNOTE가 자동 생성된다.

# Request

## Headers

- `Content-Type: application/json`
- `Accept: application/json`
- `Authorization: Bearer {accessToken}`

## Body

```json
{
  "questionId": 101,
  "selectedIndex": 2,
  "durationMs": 20000
}
```

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| questionId | integer | O | 풀이한 문제 ID |
| selectedIndex | integer | O | 선택한 선지 인덱스 (0-based) |
| durationMs | integer | X | 풀이 소요 시간 (밀리초) |

# Response

## 201 Created

```json
{
  "id": 5001,
  "questionId": 101,
  "selectedIndex": 2,
  "durationMs": 20000,
  "userId": 1,
  "anonSessionId": null,
  "isCorrect": false,
  "createdAt": "2025-07-14T09:00:00"
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

## 404 Not Found

```json
{
  "code": "QUESTION_NOT_FOUND",
  "message": "문제를 찾을 수 없습니다."
}
```

## 500 Internal Server Error

```json
{
  "code": "INTERNAL_SERVER_ERROR",
  "message": "서버 내부 오류가 발생했습니다."
}
```
