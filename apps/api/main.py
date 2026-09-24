from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from apps.api.core.config import settings
from apps.api.routes.auth import router as auth_router
from apps.api.routes.users import router as users_router
from apps.api.routes.lessons import router as lessons_router
from apps.api.routes.quizzes import router as quizzes_router
from apps.api.routes.exercises import router as exercises_router
from apps.api.routes.quiz_attempts import router as quiz_attempts_router
from apps.api.routes.exercise_attempts import router as exercise_attempts_router
from apps.api.routes.generation_jobs import router as generation_jobs_router
from apps.api.routes.progress import router as progress_router

app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(lessons_router)
app.include_router(quizzes_router)
app.include_router(exercises_router)
app.include_router(quiz_attempts_router)
app.include_router(exercise_attempts_router)
app.include_router(generation_jobs_router)
app.include_router(progress_router)

# Mount static asset directory
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/login", response_class=FileResponse)
async def login_page():
    return FileResponse(STATIC_DIR / "login.html")


@app.get("/register", response_class=FileResponse)
async def register_page():
    return FileResponse(STATIC_DIR / "login.html")


@app.get("/dashboard", response_class=FileResponse)
async def dashboard_page():
    return FileResponse(STATIC_DIR / "dashboard.html")


