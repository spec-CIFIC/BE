# 진단 풀이 제출

HTTP 메서드: POST
HTTP 상태코드: 201 Created, 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Server Error
URL Path: /api/v1/intro/attempts
버전: V1
분류: Intro
액세스 토큰 필요: X (세션 토큰 필요)

> 진단 문제 하나에 대한 풀이를 제출한다. 정오 결과와 해설을 즉시 반환한다.

# Request

## Headers

- `Content-Type: application/json`
- `Accept: application/json`
- `X-Session-Token: {sessionToken}`

## Body

```json
{
  "questionId": 101,
  "selectedIndex": 2,
  "durationMs": 15000
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
  "isCorrect": true,
  "explanation": "감가상각 방법에는 정액법, 정률법, 생산량비례법 등이 있으며 총평균법은 재고자산 평가 방법입니다."
}
```

| 필드 | 타입 | 설명 |
|---|---|---|
| id | integer | 생성된 풀이 기록 ID |
| isCorrect | boolean | 정답 여부 |
| explanation | string \| null | 해설 |

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
