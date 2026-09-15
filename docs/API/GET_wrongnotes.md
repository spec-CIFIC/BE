# 전체 오답노트 목록 조회

HTTP 메서드: GET
HTTP 상태코드: 200 OK, 401 Unauthorized, 500 Internal Server Error
URL Path: /api/v1/wrongnotes
버전: V1
분류: Wrongnote
액세스 토큰 필요: O

> 복습 예정 여부와 관계없이 전체 오답노트를 조회한다.  
> 복습 예정 오답노트는 `GET /api/v1/review/wrongnotes` 참고.

# Request

## Headers

- `Authorization: Bearer {accessToken}`
- `Accept: application/json`

## Query Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|---|---|---|---|
| q | string | X | 과목명·개념명·문제 본문 텍스트 검색 |
| subjectId | integer | X | 과목 ID로 필터 |
| isFavorited | boolean | X | `true`: 즐겨찾기만 / `false`: 비즐겨찾기만 |

# Response

## 200 OK

```json
[
  {
    "wrongnoteId": 201,
    "questionId": 101,
    "subjectId": 1,
    "subjectName": "재무회계",
    "conceptId": 3,
    "conceptName": "현재가치",
    "stem": "다음 중 현재가치 계산에 사용하는 할인율은?",
    "choices": ["명목이자율", "실질이자율", "유효이자율", "표시이자율"],
    "answerIndex": 2,
    "userAnswer": 0,
    "explanation": "현재가치 계산에는 유효이자율을 사용합니다.",
    "mistakeType": "개념 혼동",
    "userMemo": null,
    "reviewDueAt": "2025-07-21T00:00:00",
    "wrongCount": 2,
    "updatedAt": "2025-07-14T09:00:00",
    "isStudyPlan": true,
    "isFavorited": true
  }
]
```

응답 필드는 `GET /api/v1/review/wrongnotes`와 동일하다.

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
