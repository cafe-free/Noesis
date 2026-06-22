from fastapi import APIRouter, HTTPException
from core.db import supabase
from models.user import User

router = APIRouter()

@router.get("/users")
async def get_users():
    users = supabase.table("users").select("*").execute()
    if not users.data:
        raise HTTPException(status_code=404, detail="Users not found")
    return users.data

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    users = supabase.table("users").select("*").eq("id", user_id).execute()
    if not users.data:
        raise HTTPException(status_code=404, detail="User not found")
    return users.data[0]

@router.post("/users")
async def create_user(user: User):
    user = supabase.table("users").insert(user.model_dump()).execute()
    if not user.data:
        raise HTTPException(status_code=400, detail="Failed to create user")
    return {
        "message": "User created successfully",
        "user": user.data[0]
    }

@router.put("/users/{user_id}")
async def update_user(user_id: int, user: User):
    user = supabase.table("users").update(user.model_dump()).eq("id", user_id).execute()
    if not user.data:
        raise HTTPException(status_code=400, detail="Failed to update user")
    return {
        "message": "User updated successfully",
        "user": user.data[0]
    }

@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    user = supabase.table("users").delete().eq("id", user_id).execute()
    if not user.data:
        raise HTTPException(status_code=400, detail="Failed to delete user")
    return {
        "message": "User deleted successfully",
        "user": user.data[0]
    }