from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from apps.api.core.auth import (
    get_current_user,
    hash_password,
    invalid_credentials,
    issue_tokens,
    rotate_refresh_token,
    revoke_refresh_token,
    verify_password,
)
from apps.api.core.db import get_supabase
from apps.api.schemas.user import (
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UserRegistration,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _public_user(user: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in user.items() if key != "password_hash"}


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegistration, db: Client = Depends(get_supabase)):
    email = str(user_in.email).lower()
    existing = db.table("users").select("id").eq("email", email).execute()
    if existing.data:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

    result = db.table("users").insert(
        {
            "email": email,
            "username": user_in.username,
            "password_hash": hash_password(user_in.password),
            "auth_provider": "password",
        }
    ).execute()
    if not result.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to register user")
    user_id = str(result.data[0]["id"])
    db.table("user_identities").insert(
        {"user_id": user_id, "provider": "password", "provider_subject": email}
    ).execute()
    return issue_tokens(db, user_id)


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Client = Depends(get_supabase)):
    result = db.table("users").select("*").eq("email", str(credentials.email).lower()).execute()
    user = result.data[0] if result.data else None
    if not user or not user.get("password_hash") or not verify_password(credentials.password, user["password_hash"]):
        raise invalid_credentials()
    return issue_tokens(db, str(user["id"]))


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: RefreshRequest, db: Client = Depends(get_supabase)):
    return rotate_refresh_token(db, request.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: RefreshRequest, db: Client = Depends(get_supabase)):
    revoke_refresh_token(db, request.refresh_token)


@router.get("/me", response_model=UserResponse)
def current_user(user: Dict[str, Any] = Depends(get_current_user)):
    return _public_user(user)
