from fastapi import APIRouter
from apps.api.schemas.progress import BasicStatisticsResponse, WeaknessesResponse
from apps.api.db.supabase import get_supabase
from uuid import UUID

router = APIRouter(prefix="/progress", tags=["progress"])

@router.get("/{user_id}", response_model=BasicStatisticsResponse)
async def get_progress(user_id: UUID):
    supabase = get_supabase()
    
    # Get user attempts
    attempts_res = supabase.table("quiz_attempts").select("*").eq("user_id", str(user_id)).execute()
    attempts = attempts_res.data
    
    total_quizzes = len(attempts)
    completed_quizzes = len([a for a in attempts if a.get("completed_at")])
    total_exercises = sum([a.get("total_questions", 0) for a in attempts])
    correct_answers = sum([a.get("correct_answers", 0) for a in attempts])
    
    accuracy = correct_answers / total_exercises if total_exercises > 0 else 0.0
    
    return BasicStatisticsResponse(
        total_quizzes=total_quizzes,
        completed_quizzes=completed_quizzes,
        total_exercises=total_exercises,
        correct_answers=correct_answers,
        accuracy=accuracy
    )

@router.get("/{user_id}/weaknesses", response_model=WeaknessesResponse)
async def get_weaknesses(user_id: UUID):
    # Dummy implementation for now to satisfy MVP requirements
    return WeaknessesResponse(weaknesses=[
        {"topic": "present tense", "accuracy": 0.54},
        {"topic": "food vocabulary", "accuracy": 0.62}
    ])
