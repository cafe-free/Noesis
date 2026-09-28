from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExerciseAttemptBase(BaseModel):
    quiz_attempt_id: UUID
    exercise_id: UUID
    answer: str | None = None
    is_correct: bool | None = None
    response_time_ms: int | None = None


class ExerciseAttemptCreate(ExerciseAttemptBase):
    pass


class ExerciseAttemptUpdate(BaseModel):
    answer: str | None = None
    is_correct: bool | None = None
    response_time_ms: int | None = None


class ExerciseAttemptInDB(ExerciseAttemptBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExerciseAttemptResponse(ExerciseAttemptInDB):
    prompt: str | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    concept: str | None = None
