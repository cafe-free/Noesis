from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from apps.api.schemas.exercise_attempt import ExerciseAttemptResponse


class QuizAttemptBase(BaseModel):
    user_id: UUID
    quiz_id: UUID
    score: float | None = None
    total_questions: int | None = None
    correct_answers: int | None = None
    completed_at: datetime | None = None


class QuizAttemptCreate(BaseModel):
    quiz_id: UUID
    user_id: UUID | None = None
    score: float | None = None
    total_questions: int | None = None
    correct_answers: int | None = None
    completed_at: datetime | None = None
    time_spent_seconds: int | None = None
    mistakes: list[dict] | None = None
    answers: list[dict] | None = None


class QuizAttemptUpdate(BaseModel):
    score: float | None = None
    total_questions: int | None = None
    correct_answers: int | None = None
    completed_at: datetime | None = None


class QuizAttemptInDB(QuizAttemptBase):
    id: UUID
    started_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuizAttemptResponse(QuizAttemptInDB):
    exercise_attempts: list[ExerciseAttemptResponse] = []
    quiz_title: str | None = None
    language: str | None = None
