from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LessonBase(BaseModel):
    language: str
    level: str
    topic: str
    title: str
    description: str | None = None


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    language: str | None = None
    level: str | None = None
    topic: str | None = None
    title: str | None = None
    description: str | None = None


class LessonInDB(LessonBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LessonResponse(LessonInDB):
    pass
