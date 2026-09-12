from fastapi import FastAPI
from apps.api.core.config import settings
from apps.api.routes.users import router as users_router
from apps.api.routes.lessons import router as lessons_router
from apps.api.routes.quizzes import router as quizzes_router
from apps.api.routes.exercises import router as exercises_router
from apps.api.routes.quiz_attempts import router as quiz_attempts_router
from apps.api.routes.exercise_attempts import router as exercise_attempts_router
from apps.api.routes.generation_jobs import router as generation_jobs_router

app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0")


app.include_router(users_router)
app.include_router(lessons_router)
app.include_router(quizzes_router)
app.include_router(exercises_router)
app.include_router(quiz_attempts_router)
app.include_router(exercise_attempts_router)
app.include_router(generation_jobs_router)

@app.get("/")
async def root():
    return {"message": "Hello from Noesis!"}

