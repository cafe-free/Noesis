import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from supabase import Client

from apps.api.core.config import settings
from apps.api.core.db import get_supabase


bearer_scheme = HTTPBearer(auto_error=False)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived_key = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return "scrypt$16384$8$1${}${}".format(
        base64.urlsafe_b64encode(salt).decode(),
        base64.urlsafe_b64encode(derived_key).decode(),
    )


def verify_password(password: str, encoded_password: str) -> bool:
    try:
        scheme, n, r, p, encoded_salt, encoded_key = encoded_password.split("$", 5)
        if scheme != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(encoded_salt.encode())
        expected_key = base64.urlsafe_b64decode(encoded_key.encode())
        actual_key = hashlib.scrypt(
            password.encode(), salt=salt, n=int(n), r=int(r), p=int(p)
        )
        return hmac.compare_digest(actual_key, expected_key)
    except (ValueError, TypeError):
        return False


def _hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(user_id: str) -> tuple[str, int]:
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    now = _now()
    payload = {
        "sub": user_id,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM), expires_in


def create_refresh_token(db: Client, user_id: str) -> str:
    raw_token = secrets.token_urlsafe(48)
    expires_at = _now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db.table("refresh_tokens").insert(
        {
            "token_hash": _hash_refresh_token(raw_token),
            "user_id": user_id,
            "expires_at": expires_at.isoformat(),
        }
    ).execute()
    return raw_token


def issue_tokens(db: Client, user_id: str) -> Dict[str, Any]:
    access_token, expires_in = create_access_token(user_id)
    refresh_token = create_refresh_token(db, user_id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": expires_in,
    }


def revoke_refresh_token(db: Client, raw_token: str) -> None:
    db.table("refresh_tokens").update({"revoked_at": _now().isoformat()}).eq(
        "token_hash", _hash_refresh_token(raw_token)
    ).execute()


def rotate_refresh_token(db: Client, raw_token: str) -> Dict[str, Any]:
    result = db.table("refresh_tokens").select("*").eq(
        "token_hash", _hash_refresh_token(raw_token)
    ).execute()
    if not result.data:
        raise invalid_credentials()

    stored = result.data[0]
    try:
        expires_at = datetime.fromisoformat(stored["expires_at"].replace("Z", "+00:00"))
    except (KeyError, TypeError, ValueError):
        raise invalid_credentials()
    if stored.get("revoked_at") or expires_at <= _now():
        raise invalid_credentials()

    revoke_refresh_token(db, raw_token)
    return issue_tokens(db, str(stored["user_id"]))


def invalid_credentials() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


def authentication_required(detail: str = "Not authenticated") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Client = Depends(get_supabase),
) -> Dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise authentication_required()
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access" or not payload.get("sub"):
            raise JWTError()
        user_id = str(payload["sub"])
    except JWTError:
        raise authentication_required("Invalid or expired access token")

    result = db.table("users").select("*").eq("id", user_id).execute()
    if not result.data:
        raise authentication_required("User no longer exists")
    return result.data[0]
