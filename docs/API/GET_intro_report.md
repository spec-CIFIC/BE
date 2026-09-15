# 진단 리포트 조회

HTTP 메서드: GET
HTTP 상태코드: 200 OK, 400 Bad Request, 401 Unauthorized, 500 Internal Server Error
URL Path: /api/v1/intro/report
버전: V1
분류: Intro
액세스 토큰 필요: X (세션 토큰 필요)

> 진단 완료 후 호출. 자가 진단으로 예측한 약점과 실제 문제 풀이 결과를 비교해 반환한다.

# Request

## Headers

- `Accept: application/json`
- `X-Session-Token: {sessionToken}`

# Response

## 200 OK

```json
{
  "predictedWeak": [
    { "conceptId": 1, "conceptName": "감가상각" },
    { "conceptId": 3, "conceptName": "현재가치" }
  ],
  "actualResults": [
    {
      "conceptId": 1,
      "conceptName": "감가상각",
      "correct": 1,
      "total": 2,
      "accuracy": 0.5
    },
    {
      "conceptId": 2,
      "conceptName": "원가계산",
      "correct": 2,
      "total": 2,
      "accuracy": 1.0
    },
    {
      "conceptId": 3,
      "conceptName": "현재가치",
      "correct": 0,
      "total": 2,
      "accuracy": 0.0
    }
  ]
}
```

| 필드 | 타입 | 설명 |
|---|---|---|
| predictedWeak | object[] | 자가 진단에서 약하다고 선택한 개념 목록 |
| actualResults | object[] | 개념별 실제 풀이 정확도 |
| actualResults[].correct | integer | 맞힌 문제 수 |
| actualResults[].total | integer | 해당 개념 출제 문제 수 |
| actualResults[].accuracy | float | 정확도 (0.0~1.0) |

## 400 Bad Request

```json
{
  "code": "SESSION_TOKEN_REQUIRED",
  "message": "세션 토큰이 필요합니다."
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
