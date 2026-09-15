# 문제 단건 조회

HTTP 메서드: GET
HTTP 상태코드: 200 OK, 404 Not Found, 500 Internal Server Error
URL Path: /api/v1/questions/{question_id}
버전: V1
분류: Question
액세스 토큰 필요: X (선택 사항)

# Request

## Headers

- `Accept: application/json`
- `Authorization: Bearer {accessToken}` (선택)

## Path Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|---|---|---|---|
| question_id | integer | O | 조회할 문제 ID |

# Response

## 200 OK

```json
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
