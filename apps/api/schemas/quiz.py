from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from apps.api.schemas.exercise import ExerciseResponse


class QuizBase(BaseModel):
    language: str
    level: str
    topic: str
    title: str
    lesson_id: Optional[UUID] = None


class QuizCreate(QuizBase):
    pass


class QuizUpdate(BaseModel):
    language: Optional[str] = None
    level: Optional[str] = None
    topic: Optional[str] = None
    title: Optional[str] = None
    lesson_id: Optional[UUID] = None


class QuizInDB(QuizBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuizResponse(QuizBase):
    id: UUID
    created_at: datetime
    exercises: List[ExerciseResponse] = []

    model_config = ConfigDict(from_attributes=True)

