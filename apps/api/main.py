from fastapi import FastAPI, HTTPException
from data import users
from core.db import supabase
from routes.users import router as users_router

app = FastAPI()

app.include_router(users_router)

@app.get("/")
async def root():
    return {"message": "Hello from Noesis!"}
