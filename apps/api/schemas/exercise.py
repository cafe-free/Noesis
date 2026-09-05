from pydantic import BaseModel, Field
from typing import List, Literal, Union, Dict, Any
from uuid import UUID
from datetime import datetime

class MCQTranslationPayload(BaseModel):
    source_text: str
    choices: List[str]
    correct_answer: str

class FillBlankPayload(BaseModel):
    sentence: str
    correct_answer: str
    acceptable_answers: List[str]

class WordOrderPayload(BaseModel):
    tokens: List[str]
    correct_order: List[str]

class MatchingPair(BaseModel):
    left: str
    right: str

class MatchingPayload(BaseModel):
    pairs: List[MatchingPair]

# Union for the DB exercise payload
ExercisePayloadType = Union[MCQTranslationPayload, FillBlankPayload, WordOrderPayload, MatchingPayload]

class ExerciseBase(BaseModel):
    type: Literal["mcq_translation", "fill_blank", "word_order", "matching"]
    position: int
    prompt: str
    payload: Dict[str, Any] # Or union of dict representations

class ExerciseCreate(ExerciseBase):
    quiz_id: UUID

class ExerciseInDB(ExerciseBase):
    id: UUID
    quiz_id: UUID
    created_at: datetime
    
    # Validation helper to parse payload to correct schema if needed
    
class ExerciseResponse(BaseModel):
    id: UUID
    type: str
    position: int
    prompt: str
    payload: Dict[str, Any]
    
    # Hide correct answers from payload in response
    @classmethod
    def sanitize(cls, exercise: 'ExerciseInDB') -> 'ExerciseResponse':
        payload = exercise.payload.copy()
        if exercise.type == "mcq_translation":
            payload.pop("correct_answer", None)
        elif exercise.type == "fill_blank":
            payload.pop("correct_answer", None)
            payload.pop("acceptable_answers", None)
        elif exercise.type == "word_order":
            payload.pop("correct_order", None)
        return cls(
            id=exercise.id,
            type=exercise.type,
            position=exercise.position,
            prompt=exercise.prompt,
            payload=payload
        )
