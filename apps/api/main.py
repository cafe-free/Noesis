from fastapi import FastAPI, HTTPException

app = FastAPI()

users = [
    {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "password",
    },
    {
        "id": 2,
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "password": "password",
    },
    {
        "id": 3,
        "name": "John Smith",
        "email": "john.smith@example.com",
        "password": "password",
    },
    {
        "id": 4,
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "password": "password",
    },
    {
        "id": 5,
        "name": "Jim Beam",
        "email": "jim.beam@example.com",
        "password": "password",
    },
]

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