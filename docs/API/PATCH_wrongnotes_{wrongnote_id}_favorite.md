# 오답노트 즐겨찾기 토글

HTTP 메서드: PATCH
HTTP 상태코드: 204 No Content, 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Server Error
URL Path: /api/v1/wrongnotes/{wrongnote_id}/favorite
버전: V1
분류: Wrongnote
액세스 토큰 필요: O

# Request

## Headers

- `Content-Type: application/json`
- `Accept: application/json`
- `Authorization: Bearer {accessToken}`

## Path Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|---|---|---|---|
| wrongnote_id | integer | O | 대상 오답노트 ID |

## Body

```json
{
  "isFavorited": true
}
```

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| isFavorited | boolean | O | `true`: 즐겨찾기 ON / `false`: 즐겨찾기 OFF |

# Response

## 204 No Content

응답 바디 없음.

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

## 404 Not Found

```json
{
  "code": "WRONGNOTE_NOT_FOUND",
  "message": "오답노트를 찾을 수 없습니다."
}
```

## 500 Internal Server Error

```json
{
  "code": "INTERNAL_SERVER_ERROR",
  "message": "서버 내부 오류가 발생했습니다."
}
```
