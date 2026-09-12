from datetime import datetime
from typing import Literal, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

JobStatusLiteral = Literal["pending", "in_progress", "completed", "failed"]


class GenerationJobBase(BaseModel):
    language: str
    level: str
    topic: str
    count: int = Field(ge=1, description="Number of exercises/questions to generate")


class GenerationJobCreate(GenerationJobBase):
    quiz_id: Optional[UUID] = None


class GenerationJobUpdate(BaseModel):
    status: Optional[JobStatusLiteral] = None
    quiz_id: Optional[UUID] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class GenerationJobInDB(GenerationJobBase):
    id: UUID
    status: str
    quiz_id: Optional[UUID] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class GenerationJobResponse(GenerationJobInDB):
    pass
