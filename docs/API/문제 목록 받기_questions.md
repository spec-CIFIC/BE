# 문제 목록 조회

HTTP 메서드: GET
HTTP 상태코드: 200 OK, 400 Bad Request, 500 Internal Server Error
URL Path: /api/v1/questions
버전: V1
분류: Question
액세스 토큰 필요: X (선택 사항)

# Request

## Headers

- `Accept: application/json`
- `Authorization: Bearer {accessToken}` (선택)

## Query Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|---|---|---|---|
| concept_id | integer | X | 개념 ID로 필터 |
| filter | string | X | `verbal`: 말문제 / `past_exam`: 기출 문제만 |
| limit | integer | X | 최대 반환 수 (기본 20, 최대 100) |
| offset | integer | X | 페이지네이션 시작 오프셋 (기본 0) |

# Response

## 200 OK

```json
[
  {
    "id": 101,
    "subjectId": 1,
    "conceptId": 3,
    "stem": "다음 중 감가상각 방법으로 옳지 않은 것은?",
    "choices": ["정액법", "정률법", "생산량비례법", "총평균법"],
    "answerIndex": 3,
    "explanation": "총평균법은 재고자산 평가 방법입니다.",
    "questionType": "CALCULATION",
    "isAiGenerated": false,
    "createdAt": "2025-07-01T12:00:00"
  }
]
```

## 400 Bad Request

```json
{
  "code": "INVALID_FILTER",
  "message": "filter는 verbal 또는 past_exam만 허용됩니다."
}
```

```json
{
  "code": "INVALID_REQUEST",
  "message": "요청 값이 올바르지 않습니다."
}
```

## 500 Internal Server Error

```json
{
  "code": "INTERNAL_SERVER_ERROR",
  "message": "서버 내부 오류가 발생했습니다."
}
```
