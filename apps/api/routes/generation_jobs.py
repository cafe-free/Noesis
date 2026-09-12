from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from apps.api.core.db import get_supabase
from apps.api.schemas.generation_job import (
    GenerationJobCreate,
    GenerationJobResponse,
    GenerationJobUpdate,
)

router = APIRouter(prefix="/generation-jobs", tags=["generation-jobs"])


@router.get("", response_model=List[GenerationJobResponse])
async def get_generation_jobs(
    status_filter: Optional[str] = None,
    quiz_id: Optional[UUID] = None,
    db: Client = Depends(get_supabase),
):
    query = db.table("generation_jobs").select("*")
    if status_filter:
        query = query.eq("status", status_filter)
    if quiz_id:
        query = query.eq("quiz_id", str(quiz_id))
    res = query.execute()
    return res.data or []


@router.get("/{job_id}", response_model=GenerationJobResponse)
async def get_generation_job(
    job_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("generation_jobs").select("*").eq("id", str(job_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation job not found")
    return res.data[0]


@router.post("", response_model=GenerationJobResponse, status_code=status.HTTP_201_CREATED)
async def create_generation_job(
    job_in: GenerationJobCreate,
    db: Client = Depends(get_supabase),
):
    payload = job_in.model_dump(mode="json")
    payload["status"] = "pending"
    res = db.table("generation_jobs").insert(payload).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create generation job")
    return res.data[0]


@router.put("/{job_id}", response_model=GenerationJobResponse)
async def update_generation_job(
    job_id: UUID,
    job_in: GenerationJobUpdate,
    db: Client = Depends(get_supabase),
):
    payload = job_in.model_dump(exclude_unset=True, mode="json")
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")
    res = db.table("generation_jobs").update(payload).eq("id", str(job_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation job not found or update failed")
    return res.data[0]


@router.delete("/{job_id}")
async def delete_generation_job(
    job_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("generation_jobs").delete().eq("id", str(job_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation job not found or delete failed")
    return {"message": "Generation job deleted successfully", "id": str(job_id)}
