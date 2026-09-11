from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field, model_validator


# --- Payload Models ---

class MultipleChoicePayload(BaseModel):
    options: List[str]
    correct_answer: str


class FillInBlankPayload(BaseModel):
    correct_answer: str
    hint: Optional[str] = None


class WordOrderPayload(BaseModel):
    tokens: List[str]
    correct_order: List[str]


class MatchingPair(BaseModel):
    left: str
    right: str


class MatchingPayload(BaseModel):
    pairs: List[MatchingPair]


# Tagged Union for payload schemas
ExercisePayloadType = Union[
    MultipleChoicePayload,
    FillInBlankPayload,
    WordOrderPayload,
    MatchingPayload,
]


# --- Base & DB Schemas ---

class ExerciseBase(BaseModel):
    type: Literal["multiple_choice", "fill_in_blank", "word_order", "matching"]
    position: int = Field(ge=1, description="1-based position index in the quiz")
    prompt: str
    payload: Dict[str, Any]

    @model_validator(mode="after")
    def validate_payload_matches_type(self) -> "ExerciseBase":
        """Ensures payload dictionary aligns with the expected payload schema."""
        type_to_model = {
            "multiple_choice": MultipleChoicePayload,
            "fill_in_blank": FillInBlankPayload,
            "word_order": WordOrderPayload,
            "matching": MatchingPayload,
        }
        target_model = type_to_model.get(self.type)
        if target_model:
            validated_payload = target_model.model_validate(self.payload)
            self.payload = validated_payload.model_dump()
        return self


class ExerciseCreate(ExerciseBase):
    quiz_id: UUID


class ExerciseInDB(ExerciseBase):
    id: UUID
    quiz_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

    def parsed_payload(self) -> ExercisePayloadType:
        """Helper method to parse the raw payload dict into its typed model."""
        payload_map = {
            "multiple_choice": MultipleChoicePayload,
            "fill_in_blank": FillInBlankPayload,
            "word_order": WordOrderPayload,
            "matching": MatchingPayload,
        }
        return payload_map[self.type].model_validate(self.payload)


# --- Public API Response Schema ---

class ExerciseResponse(BaseModel):
    id: UUID
    type: str
    position: int
    prompt: str
    payload: Dict[str, Any]

    @classmethod
    def sanitize(cls, exercise: ExerciseInDB) -> "ExerciseResponse":
        """Strips correct answer key(s) from payload before sending to client."""
        payload = exercise.payload.copy()

        if exercise.type in ("multiple_choice", "fill_in_blank"):
            payload.pop("correct_answer", None)

        elif exercise.type == "word_order":
            payload.pop("correct_order", None)

        elif exercise.type == "matching":
            pairs = payload.get("pairs", [])
            payload = {
                "left_items": [p["left"] for p in pairs if isinstance(p, dict)],
                "right_items": [p["right"] for p in pairs if isinstance(p, dict)],
            }

        return cls(
            id=exercise.id,
            type=exercise.type,
            position=exercise.position,
            prompt=exercise.prompt,
            payload=payload,
        )