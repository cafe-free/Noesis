from pydantic import BaseModel
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime

class ExerciseAnswer(BaseModel):
    exercise_id: UUID
    answer: Any # Can be string or list depending on exercise type
    response_time_ms: int

class AnswerSubmissionRequest(BaseModel):
    user_id: UUID
    quiz_id: UUID
    answers: List[ExerciseAnswer]

class ExerciseResult(BaseModel):
    exercise_id: UUID
    is_correct: bool

class AnswerSubmissionResponse(BaseModel):
    attempt_id: UUID
    score: float
    correct_answers: int
    total_questions: int
    results: List[ExerciseResult]
