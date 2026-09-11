from fastapi import FastAPI
from apps.api.routes.users import router as users_router
from apps.api.routes.quizzes import router as quizzes_router

app = FastAPI()

app.include_router(users_router)
app.include_router(quizzes_router)

@app.get("/")
async def root():
    return {"message": "Hello from Noesis!"}
