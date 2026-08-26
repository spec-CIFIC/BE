# JWT 토큰 발급 가이드

CIFIC API는 인증이 필요한 모든 엔드포인트에 Supabase에서 발급한 JWT 토큰을 사용한다.
`Authorization: Bearer <token>` 헤더로 전달한다.

---

## 토큰 발급 (로그인)

Supabase Auth REST API에 직접 요청해 access_token을 발급받는다.

**Endpoint**
```
POST https://neaiupzzglzeypwiglnt.supabase.co/auth/v1/token?grant_type=password
```

**Headers**
```
apikey: <SUPABASE_ANON_KEY>
Content-Type: application/json
```

**Body**
```json
{
  "email": "your@email.com",
  "password": "yourpassword"
}
```

**Response**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "..."
}
```

발급받은 `access_token`을 이후 모든 API 요청의 헤더에 포함한다.

```
Authorization: Bearer eyJhbGci...
```

---

## Postman 설정 방법

1. Postman에서 로그인 요청을 보낸 뒤 응답의 `access_token` 값을 복사한다.
2. 이후 요청의 **Authorization 탭 → Type: Bearer Token** 에 붙여넣는다.

또는 Environment Variable로 관리하면 편하다.

1. Postman 상단 **Environments** → New Environment (`cific-local` 등) 생성
2. Variable: `token` / Initial Value: (비워둠)
3. 로그인 요청의 **Tests 탭**에 아래 스크립트 추가:
    ```js
    pm.environment.set("token", pm.response.json().access_token);
    ```
4. 이후 모든 요청의 Authorization 헤더를 `Bearer {{token}}`으로 설정

---

## 토큰 만료 및 갱신

- `access_token` 유효기간: **1시간** (Supabase 기본값)
- 만료 후 재로그인하거나 `refresh_token`으로 갱신한다.

**갱신 요청**
```
POST https://neaiupzzglzeypwiglnt.supabase.co/auth/v1/token?grant_type=refresh_token
```
```json
{
  "refresh_token": "..."
}
```

---

## 토큰 검증 실패 시 에러

| 상황 | HTTP | code |
|---|---|---|
| 헤더 없음 | 401 | `UNAUTHORIZED` |
| 토큰 만료·변조 | 401 | `INVALID_TOKEN` |
