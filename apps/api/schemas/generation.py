from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class GenerationJobCreateRequest(BaseModel):
    language: str
    level: str
    topic: str
    count: int

class GenerationJobCreateResponse(BaseModel):
    job_id: UUID

class GenerationJobResponse(BaseModel):
    id: UUID
    status: str
    language: str
    level: str
    topic: str
    count: int
    quiz_id: Optional[UUID] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class CurriculumSchema(BaseModel):
    language: str
    level: str
    topic: str
    learning_objectives: List[str]
    vocabulary: List[str]
    grammar: List[str]

class QAValidationResult(BaseModel):
    valid: bool
    issues: List[str] = []
