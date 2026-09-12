from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from apps.api.core.db import get_supabase
from apps.api.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserResponse])
async def get_users(
    email: Optional[str] = None,
    db: Client = Depends(get_supabase),
):
    query = db.table("users").select("*")
    if email:
        query = query.eq("email", email)
    res = query.execute()
    return res.data or []


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("users").select("*").eq("id", str(user_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return res.data[0]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: Client = Depends(get_supabase),
):
    payload = user_in.model_dump(mode="json")
    res = db.table("users").insert(payload).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create user")
    return res.data[0]


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    db: Client = Depends(get_supabase),
):
    payload = user_in.model_dump(exclude_unset=True, mode="json")
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")
    res = db.table("users").update(payload).eq("id", str(user_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or update failed")
    return res.data[0]


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("users").delete().eq("id", str(user_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or delete failed")
    return {"message": "User deleted successfully", "id": str(user_id)}

