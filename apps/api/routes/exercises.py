from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from apps.api.core.db import get_supabase
from apps.api.schemas.exercise import (
    ExerciseCreate,
    ExerciseInDB,
    ExerciseResponse,
    ExerciseUpdate,
)

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=List[ExerciseResponse])
async def get_exercises(
    quiz_id: Optional[UUID] = None,
    db: Client = Depends(get_supabase),
):
    query = db.table("exercises").select("*")
    if quiz_id:
        query = query.eq("quiz_id", str(quiz_id))
    query = query.order("position")
    res = query.execute()
    raw_exercises = res.data or []
    return [ExerciseResponse.sanitize(ExerciseInDB(**ex)) for ex in raw_exercises]


@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(
    exercise_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("exercises").select("*").eq("id", str(exercise_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    exercise_in_db = ExerciseInDB(**res.data[0])
    return ExerciseResponse.sanitize(exercise_in_db)


@router.post("", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
async def create_exercise(
    exercise_in: ExerciseCreate,
    db: Client = Depends(get_supabase),
):
    payload = exercise_in.model_dump(mode="json")
    res = db.table("exercises").insert(payload).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create exercise")
    exercise_in_db = ExerciseInDB(**res.data[0])
    return ExerciseResponse.sanitize(exercise_in_db)


@router.put("/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise(
    exercise_id: UUID,
    exercise_in: ExerciseUpdate,
    db: Client = Depends(get_supabase),
):
    payload = exercise_in.model_dump(exclude_unset=True, mode="json")
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")
    res = db.table("exercises").update(payload).eq("id", str(exercise_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found or update failed")
    exercise_in_db = ExerciseInDB(**res.data[0])
    return ExerciseResponse.sanitize(exercise_in_db)


@router.delete("/{exercise_id}")
async def delete_exercise(
    exercise_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("exercises").delete().eq("id", str(exercise_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found or delete failed")
    return {"message": "Exercise deleted successfully", "id": str(exercise_id)}
