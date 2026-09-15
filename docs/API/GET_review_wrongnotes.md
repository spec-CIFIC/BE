# 에빙하우스 복습 예정 오답노트 목록

HTTP 메서드: GET
HTTP 상태코드: 200 OK, 401 Unauthorized, 500 Internal Server Error
URL Path: /api/v1/review/wrongnotes
버전: V1
분류: Review
액세스 토큰 필요: O

> `WRONGNOTE.reviewDueAt ≤ now`인 오답노트만 반환한다 (복습 예정분).  
> 전체 오답노트 목록은 `GET /api/v1/wrongnotes` 참고.  
> STUDY_PLAN 등록 개념의 오답노트가 먼저 정렬된다.

# Request

## Headers

- `Authorization: Bearer {accessToken}`
- `Accept: application/json`

## Query Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|---|---|---|---|
| concept_id | integer | X | 특정 개념의 오답노트만 조회 (드릴다운) |

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
    "userMemo": "유효이자율과 명목이자율 차이 복습 필요",
    "reviewDueAt": "2025-07-14T00:00:00",
    "wrongCount": 2,
    "updatedAt": "2025-07-10T09:00:00",
    "isStudyPlan": true,
    "isFavorited": false
  }
]
```

| 필드 | 타입 | 설명 |
|---|---|---|
| wrongnoteId | integer | 오답노트 ID |
| questionId | integer | 문제 ID |
| subjectId / subjectName | integer / string | 과목 정보 |
| conceptId / conceptName | integer / string | 개념 정보 |
| stem | string | 문제 본문 |
| choices | string[] | 선택지 목록 |
| answerIndex | integer | 정답 인덱스 (0-based) |
| userAnswer | integer \| null | 사용자가 선택한 인덱스 |
| explanation | string \| null | 해설 |
| mistakeType | string \| null | AI가 판정한 실수 유형 |
| userMemo | string \| null | 사용자 메모 |
| reviewDueAt | datetime \| null | 다음 복습 예정 시각 |
| wrongCount | integer | 틀린 횟수 |
| isStudyPlan | boolean | 학습 계획 등록 여부 |
| isFavorited | boolean | 즐겨찾기 여부 |

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
