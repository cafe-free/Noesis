from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ExerciseAttemptBase(BaseModel):
    quiz_attempt_id: UUID
    exercise_id: UUID
    answer: Optional[str] = None
    is_correct: Optional[bool] = None
    response_time_ms: Optional[int] = None


class ExerciseAttemptCreate(ExerciseAttemptBase):
    pass


class ExerciseAttemptUpdate(BaseModel):
    answer: Optional[str] = None
    is_correct: Optional[bool] = None
    response_time_ms: Optional[int] = None


class ExerciseAttemptInDB(ExerciseAttemptBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExerciseAttemptResponse(ExerciseAttemptInDB):
    pass
