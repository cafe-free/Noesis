from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from apps.api.core.db import get_supabase
from apps.api.schemas.exercise_attempt import (
    ExerciseAttemptCreate,
    ExerciseAttemptResponse,
    ExerciseAttemptUpdate,
)

router = APIRouter(prefix="/exercise-attempts", tags=["exercise-attempts"])


@router.get("", response_model=List[ExerciseAttemptResponse])
async def get_exercise_attempts(
    quiz_attempt_id: Optional[UUID] = None,
    exercise_id: Optional[UUID] = None,
    db: Client = Depends(get_supabase),
):
    query = db.table("exercise_attempts").select("*")
    if quiz_attempt_id:
        query = query.eq("quiz_attempt_id", str(quiz_attempt_id))
    if exercise_id:
        query = query.eq("exercise_id", str(exercise_id))
    res = query.execute()
    return res.data or []


@router.get("/{attempt_id}", response_model=ExerciseAttemptResponse)
async def get_exercise_attempt(
    attempt_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("exercise_attempts").select("*").eq("id", str(attempt_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise attempt not found")
    return res.data[0]


@router.post("", response_model=ExerciseAttemptResponse, status_code=status.HTTP_201_CREATED)
async def create_exercise_attempt(
    attempt_in: ExerciseAttemptCreate,
    db: Client = Depends(get_supabase),
):
    payload = attempt_in.model_dump(mode="json")
    res = db.table("exercise_attempts").insert(payload).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create exercise attempt")
    return res.data[0]


@router.put("/{attempt_id}", response_model=ExerciseAttemptResponse)
async def update_exercise_attempt(
    attempt_id: UUID,
    attempt_in: ExerciseAttemptUpdate,
    db: Client = Depends(get_supabase),
):
    payload = attempt_in.model_dump(exclude_unset=True, mode="json")
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")
    res = db.table("exercise_attempts").update(payload).eq("id", str(attempt_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise attempt not found or update failed")
    return res.data[0]


@router.delete("/{attempt_id}")
async def delete_exercise_attempt(
    attempt_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("exercise_attempts").delete().eq("id", str(attempt_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise attempt not found or delete failed")
    return {"message": "Exercise attempt deleted successfully", "id": str(attempt_id)}
