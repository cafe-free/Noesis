from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class LessonBase(BaseModel):
    language: str
    level: str
    topic: str
    title: str
    description: Optional[str] = None


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    language: Optional[str] = None
    level: Optional[str] = None
    topic: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


class LessonInDB(LessonBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LessonResponse(LessonInDB):
    pass
