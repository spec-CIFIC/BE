# 익명 세션 데이터 회원 병합

HTTP 메서드: POST
HTTP 상태코드: 200 OK, 400 Bad Request, 401 Unauthorized, 409 Conflict, 500 Internal Server Error
URL Path: /api/v1/auth/merge
버전: V1
분류: Auth
액세스 토큰 필요: O

# Request

## Headers

- `Accept: application/json`
- `Authorization: Bearer {accessToken}`
- `X-Session-Token: {sessionToken}`

> 입문자 플로우(intro)에서 생성된 익명 세션 토큰과 로그인 토큰을 함께 전달한다.  
> 병합 성공 시 익명 세션의 풀이 기록이 해당 회원으로 이전된다.

# Response

## 200 OK

```json
{
  "message": "익명 세션이 성공적으로 병합되었습니다."
}
```

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
  "code": "UNAUTHORIZED",
  "message": "인증이 필요합니다."
}
```

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

## 409 Conflict

```json
{
  "code": "SESSION_ALREADY_MERGED",
  "message": "이미 병합된 세션입니다."
}
```

## 500 Internal Server Error

```json
{
  "code": "INTERNAL_SERVER_ERROR",
  "message": "서버 내부 오류가 발생했습니다."
}
```
