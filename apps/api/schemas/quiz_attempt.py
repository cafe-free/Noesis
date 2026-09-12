from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from apps.api.schemas.exercise_attempt import ExerciseAttemptResponse


class QuizAttemptBase(BaseModel):
    user_id: UUID
    quiz_id: UUID
    score: Optional[float] = None
    total_questions: Optional[int] = None
    correct_answers: Optional[int] = None
    completed_at: Optional[datetime] = None


class QuizAttemptCreate(BaseModel):
    user_id: UUID
    quiz_id: UUID
    total_questions: Optional[int] = None


class QuizAttemptUpdate(BaseModel):
    score: Optional[float] = None
    total_questions: Optional[int] = None
    correct_answers: Optional[int] = None
    completed_at: Optional[datetime] = None


class QuizAttemptInDB(QuizAttemptBase):
    id: UUID
    started_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuizAttemptResponse(QuizAttemptInDB):
    exercise_attempts: List[ExerciseAttemptResponse] = []
