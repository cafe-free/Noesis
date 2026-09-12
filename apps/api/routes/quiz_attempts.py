from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from apps.api.core.db import get_supabase
from apps.api.schemas.exercise_attempt import ExerciseAttemptResponse
from apps.api.schemas.quiz_attempt import (
    QuizAttemptCreate,
    QuizAttemptResponse,
    QuizAttemptUpdate,
)

router = APIRouter(prefix="/quiz-attempts", tags=["quiz-attempts"])


@router.get("", response_model=List[QuizAttemptResponse])
async def get_quiz_attempts(
    user_id: Optional[UUID] = None,
    quiz_id: Optional[UUID] = None,
    db: Client = Depends(get_supabase),
):
    query = db.table("quiz_attempts").select("*")
    if user_id:
        query = query.eq("user_id", str(user_id))
    if quiz_id:
        query = query.eq("quiz_id", str(quiz_id))
    res = query.execute()
    attempts = res.data or []
    for att in attempts:
        if "exercise_attempts" not in att:
            att["exercise_attempts"] = []
    return attempts


@router.get("/{attempt_id}", response_model=QuizAttemptResponse)
async def get_quiz_attempt(
    attempt_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("quiz_attempts").select("*").eq("id", str(attempt_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz attempt not found")
    attempt = res.data[0]

    # Fetch associated exercise attempts
    ex_res = db.table("exercise_attempts").select("*").eq("quiz_attempt_id", str(attempt_id)).execute()
    attempt["exercise_attempts"] = ex_res.data or []
    return attempt


@router.post("", response_model=QuizAttemptResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz_attempt(
    attempt_in: QuizAttemptCreate,
    db: Client = Depends(get_supabase),
):
    payload = attempt_in.model_dump(mode="json")
    res = db.table("quiz_attempts").insert(payload).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create quiz attempt")
    attempt = res.data[0]
    attempt["exercise_attempts"] = []
    return attempt


@router.put("/{attempt_id}", response_model=QuizAttemptResponse)
async def update_quiz_attempt(
    attempt_id: UUID,
    attempt_in: QuizAttemptUpdate,
    db: Client = Depends(get_supabase),
):
    payload = attempt_in.model_dump(exclude_unset=True, mode="json")
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")
    res = db.table("quiz_attempts").update(payload).eq("id", str(attempt_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz attempt not found or update failed")
    attempt = res.data[0]

    ex_res = db.table("exercise_attempts").select("*").eq("quiz_attempt_id", str(attempt_id)).execute()
    attempt["exercise_attempts"] = ex_res.data or []
    return attempt


@router.delete("/{attempt_id}")
async def delete_quiz_attempt(
    attempt_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("quiz_attempts").delete().eq("id", str(attempt_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz attempt not found or delete failed")
    return {"message": "Quiz attempt deleted successfully", "id": str(attempt_id)}
