from typing import List
from fastapi import APIRouter, HTTPException
from apps.api.schemas.quiz import QuizResponse
from apps.api.core.db import supabase
from apps.api.schemas.exercise import ExerciseResponse, ExerciseInDB
from uuid import UUID

router = APIRouter(prefix="/quizzes", tags=["quizzes"])

@router.get("", response_model=List[QuizResponse])
async def get_quizzes():
    quizzes = supabase.table("quizzes").select("*").execute()
    if not quizzes.data:
        raise HTTPException(status_code=404, detail="Quizzes not found")
    return quizzes.data

@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: UUID):

    # Get quiz
    quiz_res = supabase.table("quizzes").select("*").eq("id", str(quiz_id)).execute()
    if not quiz_res.data:
        raise HTTPException(status_code=404, detail="Quiz not found")
    quiz = quiz_res.data[0]

    # Get exercises
    ex_res = supabase.table("exercises").select("*").eq("quiz_id", str(quiz_id)).order("position").execute()
    exercises_in_db = [ExerciseInDB(**ex) for ex in ex_res.data]

    # Sanitize exercises to hide correct answers
    sanitized_exercises = [ExerciseResponse.sanitize(ex) for ex in exercises_in_db]

    quiz["exercises"] = sanitized_exercises
    return QuizResponse(**quiz)
