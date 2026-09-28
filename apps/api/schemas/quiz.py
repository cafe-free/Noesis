from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from apps.api.schemas.exercise import ExerciseResponse


class QuizBase(BaseModel):
    language: str
    level: str
    topic: str
    title: str
    lesson_id: UUID | None = None


class QuizCreate(QuizBase):
    pass


class QuizUpdate(BaseModel):
    language: str | None = None
    level: str | None = None
    topic: str | None = None
    title: str | None = None
    lesson_id: UUID | None = None


class QuizInDB(QuizBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuizResponse(QuizBase):
    id: UUID
    created_at: datetime
    exercises: list[ExerciseResponse] = []

    model_config = ConfigDict(from_attributes=True)
