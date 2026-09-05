from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from apps.api.schemas.generation import GenerationJobCreateRequest, GenerationJobCreateResponse, GenerationJobResponse
from apps.api.db.supabase import get_supabase
from apps.api.db.redis import get_redis
from uuid import UUID
import json

router = APIRouter(prefix="/generation", tags=["generation"])

@router.post("/jobs", response_model=GenerationJobCreateResponse)
async def create_generation_job(request: GenerationJobCreateRequest, background_tasks: BackgroundTasks):
    supabase = get_supabase()
    redis = await get_redis()
    
    # Create job in DB
    res = supabase.table("generation_jobs").insert({
        "status": "pending",
        "language": request.language,
        "level": request.level,
        "topic": request.topic,
        "count": request.count
    }).execute()
    
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to create job")
        
    job_id = res.data[0]["id"]
    
    # Enqueue job
    await redis.rpush("generation_jobs", json.dumps({"job_id": job_id}))
    
    return GenerationJobCreateResponse(job_id=UUID(job_id))

@router.get("/jobs/{job_id}", response_model=GenerationJobResponse)
async def get_generation_job(job_id: UUID):
    supabase = get_supabase()
    res = supabase.table("generation_jobs").select("*").eq("id", str(job_id)).execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return GenerationJobResponse(**res.data[0])
