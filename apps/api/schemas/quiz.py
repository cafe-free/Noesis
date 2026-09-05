from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from apps.api.schemas.exercise import ExerciseResponse, ExerciseInDB

class QuizBase(BaseModel):
    language: str
    level: str
    topic: str
    title: str

class QuizInDB(QuizBase):
    id: UUID
    lesson_id: Optional[UUID] = None
    created_at: datetime

class QuizResponse(QuizBase):
    id: UUID
    exercises: List[ExerciseResponse] = []
