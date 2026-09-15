# 진단 문제 목록 조회

HTTP 메서드: GET
HTTP 상태코드: 200 OK, 400 Bad Request, 401 Unauthorized, 500 Internal Server Error
URL Path: /api/v1/intro/questions
버전: V1
분류: Intro
액세스 토큰 필요: X (세션 토큰 필요)

> 자가 진단(`POST /intro/self-diagnosis`) 완료 후 호출. 정답·해설은 포함되지 않으며, 풀이 제출(`POST /intro/attempts`) 후 반환된다.

# Request

## Headers

- `Accept: application/json`
- `X-Session-Token: {sessionToken}`

# Response

## 200 OK

```json
[
  {
    "id": 101,
    "subjectId": 1,
    "conceptId": 3,
    "stem": "다음 중 감가상각 방법으로 옳지 않은 것은?",
    "choices": [
      "정액법",
      "정률법",
      "생산량비례법",
      "총평균법"
    ]
  }
]
```

| 필드 | 타입 | 설명 |
|---|---|---|
| id | integer | 문제 ID |
| subjectId | integer | 과목 ID |
| conceptId | integer | 개념 ID |
| stem | string | 문제 본문 |
| choices | string[] | 선택지 목록 |

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
