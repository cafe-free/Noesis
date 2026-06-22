from fastapi import FastAPI, HTTPException
from data import users
from core.db import supabase

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from Noesis!"}

@app.get("/users")
async def get_users():
    return users

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = next((user for user in users if user["id"] == user_id), None)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")