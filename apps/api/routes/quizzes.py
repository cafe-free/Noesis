from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from apps.api.core.db import get_supabase
from apps.api.schemas.exercise import ExerciseInDB, ExerciseResponse
from apps.api.schemas.quiz import QuizCreate, QuizResponse, QuizUpdate

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.get("", response_model=List[QuizResponse])
async def get_quizzes(
    language: Optional[str] = None,
    level: Optional[str] = None,
    topic: Optional[str] = None,
    lesson_id: Optional[UUID] = None,
    db: Client = Depends(get_supabase),
):
    query = db.table("quizzes").select("*")
    if language:
        query = query.eq("language", language)
    if level:
        query = query.eq("level", level)
    if topic:
        query = query.eq("topic", topic)
    if lesson_id:
        query = query.eq("lesson_id", str(lesson_id))
    quizzes_res = query.execute()
    quizzes = quizzes_res.data or []

    for quiz in quizzes:
        if "exercises" not in quiz:
            quiz["exercises"] = []
    return quizzes


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: UUID,
    db: Client = Depends(get_supabase),
):
    # Get quiz
    quiz_res = db.table("quizzes").select("*").eq("id", str(quiz_id)).execute()
    if not quiz_res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    quiz = quiz_res.data[0]

    # Get exercises
    ex_res = db.table("exercises").select("*").eq("quiz_id", str(quiz_id)).order("position").execute()
    raw_exercises = ex_res.data or []
    exercises_in_db = [ExerciseInDB(**ex) for ex in raw_exercises]

    # Sanitize exercises to hide correct answers
    sanitized_exercises = [ExerciseResponse.sanitize(ex) for ex in exercises_in_db]

    quiz["exercises"] = sanitized_exercises
    return QuizResponse(**quiz)


@router.post("", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    quiz_in: QuizCreate,
    db: Client = Depends(get_supabase),
):
    payload = quiz_in.model_dump(mode="json")
    res = db.table("quizzes").insert(payload).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create quiz")
    quiz = res.data[0]
    quiz["exercises"] = []
    return quiz


@router.put("/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: UUID,
    quiz_in: QuizUpdate,
    db: Client = Depends(get_supabase),
):
    payload = quiz_in.model_dump(exclude_unset=True, mode="json")
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")
    res = db.table("quizzes").update(payload).eq("id", str(quiz_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found or update failed")
    quiz = res.data[0]

    # Get existing exercises
    ex_res = db.table("exercises").select("*").eq("quiz_id", str(quiz_id)).order("position").execute()
    raw_exercises = ex_res.data or []
    sanitized_exercises = [ExerciseResponse.sanitize(ExerciseInDB(**ex)) for ex in raw_exercises]
    quiz["exercises"] = sanitized_exercises
    return quiz


@router.delete("/{quiz_id}")
async def delete_quiz(
    quiz_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("quizzes").delete().eq("id", str(quiz_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found or delete failed")
    return {"message": "Quiz deleted successfully", "id": str(quiz_id)}

