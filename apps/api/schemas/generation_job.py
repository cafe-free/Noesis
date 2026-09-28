from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

JobStatusLiteral = Literal["pending", "in_progress", "completed", "failed"]


class GenerationJobBase(BaseModel):
    language: str
    level: str
    topic: str
    count: int = Field(ge=1, description="Number of exercises/questions to generate")


class GenerationJobCreate(GenerationJobBase):
    quiz_id: UUID | None = None


class GenerationJobUpdate(BaseModel):
    status: JobStatusLiteral | None = None
    quiz_id: UUID | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class GenerationJobInDB(GenerationJobBase):
    id: UUID
    status: str
    quiz_id: UUID | None = None
    error: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class GenerationJobResponse(GenerationJobInDB):
    pass
