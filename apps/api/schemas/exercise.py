from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator


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

ExerciseTypeLiteral = Literal["multiple_choice", "fill_in_blank", "word_order", "matching"]


# --- Base & DB Schemas ---

class ExerciseBase(BaseModel):
    type: ExerciseTypeLiteral
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
        if target_model and self.payload is not None:
            validated_payload = target_model.model_validate(self.payload)
            self.payload = validated_payload.model_dump()
        return self


class ExerciseCreate(ExerciseBase):
    quiz_id: UUID


class ExerciseUpdate(BaseModel):
    type: Optional[ExerciseTypeLiteral] = None
    position: Optional[int] = Field(default=None, ge=1)
    prompt: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def validate_payload_if_present(self) -> "ExerciseUpdate":
        if self.type and self.payload is not None:
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


class ExerciseInDB(ExerciseBase):
    id: UUID
    quiz_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

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
    quiz_id: Optional[UUID] = None
    type: str
    position: int
    prompt: str
    payload: Dict[str, Any]
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def sanitize(cls, exercise: Union[ExerciseInDB, Dict[str, Any]]) -> "ExerciseResponse":
        """Strips correct answer key(s) from payload before sending to client."""
        if isinstance(exercise, dict):
            ex_id = exercise["id"]
            quiz_id = exercise.get("quiz_id")
            ex_type = exercise["type"]
            position = exercise["position"]
            prompt = exercise["prompt"]
            payload = dict(exercise.get("payload", {}))
            created_at = exercise.get("created_at")
        else:
            ex_id = exercise.id
            quiz_id = exercise.quiz_id
            ex_type = exercise.type
            position = exercise.position
            prompt = exercise.prompt
            payload = exercise.payload.copy()
            created_at = exercise.created_at

        if ex_type in ("multiple_choice", "fill_in_blank"):
            payload.pop("correct_answer", None)
        elif ex_type == "word_order":
            payload.pop("correct_order", None)
        elif ex_type == "matching":
            pairs = payload.get("pairs", [])
            payload = {
                "left_items": [p["left"] if isinstance(p, dict) else getattr(p, "left", "") for p in pairs],
                "right_items": [p["right"] if isinstance(p, dict) else getattr(p, "right", "") for p in pairs],
            }

        return cls(
            id=ex_id,
            quiz_id=quiz_id,
            type=ex_type,
            position=position,
            prompt=prompt,
            payload=payload,
            created_at=created_at,
        )