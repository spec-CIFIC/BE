import json
import urllib.request

import jwt
from jwt.algorithms import ECAlgorithm

from app.core.config import settings
from app.exception.constant.auth import AuthErrorCode
from app.exception.exception import CificException

_jwks_cache: dict[str, object] = {}


def _get_public_key(kid: str) -> object:
    if kid not in _jwks_cache:
        url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
        with urllib.request.urlopen(url) as resp:
            keys = json.loads(resp.read())["keys"]
        for k in keys:
            _jwks_cache[k["kid"]] = ECAlgorithm.from_jwk(json.dumps(k))
    return _jwks_cache.get(kid)


def verify_supabase_token(token: str) -> dict:
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        alg = header.get("alg", "ES256")
        public_key = _get_public_key(kid)
        if not public_key:
            raise CificException(AuthErrorCode.INVALID_TOKEN)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[alg],
            audience="authenticated",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise CificException(AuthErrorCode.EXPIRED_TOKEN)
    except jwt.InvalidTokenError:
        raise CificException(AuthErrorCode.INVALID_TOKEN)
