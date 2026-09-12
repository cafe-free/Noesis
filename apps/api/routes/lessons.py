from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from apps.api.core.db import get_supabase
from apps.api.schemas.lesson import LessonCreate, LessonResponse, LessonUpdate

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("", response_model=List[LessonResponse])
async def get_lessons(
    language: Optional[str] = None,
    level: Optional[str] = None,
    topic: Optional[str] = None,
    db: Client = Depends(get_supabase),
):
    query = db.table("lessons").select("*")
    if language:
        query = query.eq("language", language)
    if level:
        query = query.eq("level", level)
    if topic:
        query = query.eq("topic", topic)
    res = query.execute()
    return res.data or []


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("lessons").select("*").eq("id", str(lesson_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return res.data[0]


@router.post("", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    lesson_in: LessonCreate,
    db: Client = Depends(get_supabase),
):
    payload = lesson_in.model_dump(mode="json")
    res = db.table("lessons").insert(payload).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create lesson")
    return res.data[0]


@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: UUID,
    lesson_in: LessonUpdate,
    db: Client = Depends(get_supabase),
):
    payload = lesson_in.model_dump(exclude_unset=True, mode="json")
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")
    res = db.table("lessons").update(payload).eq("id", str(lesson_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found or update failed")
    return res.data[0]


@router.delete("/{lesson_id}")
async def delete_lesson(
    lesson_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("lessons").delete().eq("id", str(lesson_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found or delete failed")
    return {"message": "Lesson deleted successfully", "id": str(lesson_id)}
