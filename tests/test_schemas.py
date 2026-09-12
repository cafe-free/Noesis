import uuid
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from apps.api.schemas.user import (
    UserCreate,
    UserInDB,
    UserResponse,
    UserUpdate,
)
from apps.api.schemas.lesson import (
    LessonCreate,
    LessonInDB,
    LessonResponse,
    LessonUpdate,
)
from apps.api.schemas.quiz import (
    QuizCreate,
    QuizInDB,
    QuizResponse,
    QuizUpdate,
)
from apps.api.schemas.exercise import (
    ExerciseCreate,
    ExerciseInDB,
    ExerciseResponse,
    ExerciseUpdate,
    MultipleChoicePayload,
    FillInBlankPayload,
    WordOrderPayload,
    MatchingPayload,
)
from apps.api.schemas.quiz_attempt import (
    QuizAttemptCreate,
    QuizAttemptInDB,
    QuizAttemptResponse,
    QuizAttemptUpdate,
)
from apps.api.schemas.exercise_attempt import (
    ExerciseAttemptCreate,
    ExerciseAttemptInDB,
    ExerciseAttemptResponse,
    ExerciseAttemptUpdate,
)
from apps.api.schemas.generation_job import (
    GenerationJobCreate,
    GenerationJobInDB,
    GenerationJobResponse,
    GenerationJobUpdate,
)


def test_user_schemas():
    # Valid UserCreate
    user_in = UserCreate(email="alice@example.com", username="alice")
    assert user_in.email == "alice@example.com"
    assert user_in.username == "alice"

    # Invalid email in UserCreate
    with pytest.raises(ValidationError):
        UserCreate(email="not-an-email")

    # UserInDB & UserResponse
    now = datetime.now(timezone.utc)
    uid = uuid.uuid4()
    user_db = UserInDB(id=uid, email="alice@example.com", username="alice", created_at=now, updated_at=now)
    assert user_db.id == uid

    user_resp = UserResponse.model_validate(user_db)
    assert user_resp.email == "alice@example.com"


def test_lesson_schemas():
    lesson_in = LessonCreate(
        language="Spanish",
        level="A1",
        topic="Greetings",
        title="Basic Greetings",
        description="Learn basic Spanish greetings",
    )
    assert lesson_in.language == "Spanish"

    # Missing required field
    with pytest.raises(ValidationError):
        LessonCreate(language="Spanish", level="A1", topic="Greetings")  # missing title

    now = datetime.now(timezone.utc)
    lid = uuid.uuid4()
    lesson_db = LessonInDB(
        id=lid,
        language="Spanish",
        level="A1",
        topic="Greetings",
        title="Basic Greetings",
        created_at=now,
        updated_at=now,
    )
    lesson_resp = LessonResponse.model_validate(lesson_db)
    assert lesson_resp.id == lid


def test_quiz_schemas():
    lid = uuid.uuid4()
    quiz_in = QuizCreate(
        language="Spanish",
        level="A1",
        topic="Greetings",
        title="Greetings Quiz",
        lesson_id=lid,
    )
    assert quiz_in.lesson_id == lid

    now = datetime.now(timezone.utc)
    qid = uuid.uuid4()
    quiz_db = QuizInDB(
        id=qid,
        language="Spanish",
        level="A1",
        topic="Greetings",
        title="Greetings Quiz",
        lesson_id=lid,
        created_at=now,
    )
    quiz_resp = QuizResponse.model_validate(quiz_db)
    assert quiz_resp.id == qid
    assert quiz_resp.exercises == []


def test_exercise_schemas_multiple_choice():
    qid = uuid.uuid4()
    ex_in = ExerciseCreate(
        quiz_id=qid,
        type="multiple_choice",
        position=1,
        prompt="What is 'hello' in Spanish?",
        payload={
            "options": ["Hola", "Adiós", "Gracias", "Por favor"],
            "correct_answer": "Hola",
        },
    )
    assert ex_in.type == "multiple_choice"

    # Test invalid payload (missing correct_answer)
    with pytest.raises(ValidationError):
        ExerciseCreate(
            quiz_id=qid,
            type="multiple_choice",
            position=1,
            prompt="What is 'hello' in Spanish?",
            payload={"options": ["Hola", "Adiós"]},
        )

    # Test sanitize
    now = datetime.now(timezone.utc)
    eid = uuid.uuid4()
    ex_db = ExerciseInDB(
        id=eid,
        quiz_id=qid,
        type="multiple_choice",
        position=1,
        prompt="What is 'hello' in Spanish?",
        payload={
            "options": ["Hola", "Adiós", "Gracias", "Por favor"],
            "correct_answer": "Hola",
        },
        created_at=now,
    )
    sanitized = ExerciseResponse.sanitize(ex_db)
    assert "correct_answer" not in sanitized.payload
    assert sanitized.payload["options"] == ["Hola", "Adiós", "Gracias", "Por favor"]


def test_exercise_schemas_fill_in_blank():
    qid = uuid.uuid4()
    ex_in = ExerciseCreate(
        quiz_id=qid,
        type="fill_in_blank",
        position=2,
        prompt="Fill in: Buenos ___",
        payload={
            "correct_answer": "días",
            "hint": "means days",
        },
    )
    assert ex_in.type == "fill_in_blank"

    now = datetime.now(timezone.utc)
    eid = uuid.uuid4()
    ex_db = ExerciseInDB(
        id=eid,
        quiz_id=qid,
        type="fill_in_blank",
        position=2,
        prompt="Fill in: Buenos ___",
        payload={
            "correct_answer": "días",
            "hint": "means days",
        },
        created_at=now,
    )
    sanitized = ExerciseResponse.sanitize(ex_db)
    assert "correct_answer" not in sanitized.payload
    assert sanitized.payload["hint"] == "means days"


def test_exercise_schemas_word_order():
    qid = uuid.uuid4()
    ex_in = ExerciseCreate(
        quiz_id=qid,
        type="word_order",
        position=3,
        prompt="Arrange the words: How are you?",
        payload={
            "tokens": ["estás", "¿Cómo", "?"],
            "correct_order": ["¿Cómo", "estás", "?"],
        },
    )
    assert ex_in.type == "word_order"

    now = datetime.now(timezone.utc)
    eid = uuid.uuid4()
    ex_db = ExerciseInDB(
        id=eid,
        quiz_id=qid,
        type="word_order",
        position=3,
        prompt="Arrange the words",
        payload={
            "tokens": ["estás", "¿Cómo", "?"],
            "correct_order": ["¿Cómo", "estás", "?"],
        },
        created_at=now,
    )
    sanitized = ExerciseResponse.sanitize(ex_db)
    assert "correct_order" not in sanitized.payload
    assert sanitized.payload["tokens"] == ["estás", "¿Cómo", "?"]


def test_exercise_schemas_matching():
    qid = uuid.uuid4()
    ex_in = ExerciseCreate(
        quiz_id=qid,
        type="matching",
        position=4,
        prompt="Match the words with their meanings",
        payload={
            "pairs": [
                {"left": "Hola", "right": "Hello"},
                {"left": "Adiós", "right": "Goodbye"},
            ]
        },
    )
    assert ex_in.type == "matching"

    now = datetime.now(timezone.utc)
    eid = uuid.uuid4()
    ex_db = ExerciseInDB(
        id=eid,
        quiz_id=qid,
        type="matching",
        position=4,
        prompt="Match the words with their meanings",
        payload={
            "pairs": [
                {"left": "Hola", "right": "Hello"},
                {"left": "Adiós", "right": "Goodbye"},
            ]
        },
        created_at=now,
    )
    sanitized = ExerciseResponse.sanitize(ex_db)
    assert "pairs" not in sanitized.payload
    assert sanitized.payload["left_items"] == ["Hola", "Adiós"]
    assert sanitized.payload["right_items"] == ["Hello", "Goodbye"]


def test_quiz_attempt_schemas():
    uid = uuid.uuid4()
    qid = uuid.uuid4()
    attempt_in = QuizAttemptCreate(user_id=uid, quiz_id=qid, total_questions=5)
    assert attempt_in.total_questions == 5

    now = datetime.now(timezone.utc)
    aid = uuid.uuid4()
    attempt_db = QuizAttemptInDB(
        id=aid,
        user_id=uid,
        quiz_id=qid,
        score=100.0,
        total_questions=5,
        correct_answers=5,
        started_at=now,
        completed_at=now,
    )
    resp = QuizAttemptResponse.model_validate(attempt_db)
    assert resp.id == aid
    assert resp.score == 100.0


def test_exercise_attempt_schemas():
    aid = uuid.uuid4()
    eid = uuid.uuid4()
    ex_att_in = ExerciseAttemptCreate(
        quiz_attempt_id=aid,
        exercise_id=eid,
        answer="Hola",
        is_correct=True,
        response_time_ms=1200,
    )
    assert ex_att_in.is_correct is True

    now = datetime.now(timezone.utc)
    ea_id = uuid.uuid4()
    ea_db = ExerciseAttemptInDB(
        id=ea_id,
        quiz_attempt_id=aid,
        exercise_id=eid,
        answer="Hola",
        is_correct=True,
        response_time_ms=1200,
        created_at=now,
    )
    resp = ExerciseAttemptResponse.model_validate(ea_db)
    assert resp.id == ea_id
    assert resp.answer == "Hola"


def test_generation_job_schemas():
    job_in = GenerationJobCreate(
        language="Spanish",
        level="A1",
        topic="Food",
        count=5,
    )
    assert job_in.count == 5

    # Invalid count < 1
    with pytest.raises(ValidationError):
        GenerationJobCreate(
            language="Spanish",
            level="A1",
            topic="Food",
            count=0,
        )

    now = datetime.now(timezone.utc)
    jid = uuid.uuid4()
    job_db = GenerationJobInDB(
        id=jid,
        status="pending",
        language="Spanish",
        level="A1",
        topic="Food",
        count=5,
        created_at=now,
    )
    resp = GenerationJobResponse.model_validate(job_db)
    assert resp.status == "pending"
