# 학습 계획 개념 삭제

HTTP 메서드: DELETE
HTTP 상태코드: 204 No Content, 401 Unauthorized, 404 Not Found, 500 Internal Server Error
URL Path: /api/v1/study-plan/{concept_id}
버전: V1
분류: StudyPlan
액세스 토큰 필요: O

# Request

## Headers

- `Authorization: Bearer {accessToken}`

## Path Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|---|---|---|---|
| concept_id | integer | O | 삭제할 개념 ID |

# Response

## 204 No Content

응답 바디 없음.

## 401 Unauthorized

```json
{
  "code": "UNAUTHORIZED",
  "message": "인증이 필요합니다."
}
```

## 404 Not Found

```json
{
  "code": "STUDY_PLAN_NOT_FOUND",
  "message": "등록된 주요 개념이 아닙니다."
}
```

## 500 Internal Server Error

```json
{
  "code": "INTERNAL_SERVER_ERROR",
  "message": "서버 내부 오류가 발생했습니다."
}
```
