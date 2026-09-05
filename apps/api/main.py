from fastapi import FastAPI
from apps.api.routes import generation, quizzes, attempts, progress
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Noesis API",
    description="AI-powered language learning platform",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generation.router)
app.include_router(quizzes.router)
app.include_router(attempts.router)
app.include_router(progress.router)

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
