from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from apps.api.core.auth import get_current_user
from apps.api.core.db import get_supabase
from apps.api.schemas.quiz_attempt import (
    QuizAttemptCreate,
    QuizAttemptResponse,
    QuizAttemptUpdate,
)

router = APIRouter(
    prefix="/quiz-attempts",
    tags=["quiz-attempts"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[QuizAttemptResponse])
async def get_quiz_attempts(
    user_id: UUID | None = None,
    quiz_id: UUID | None = None,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_supabase),
):
    query = db.table("quiz_attempts").select("*")
    target_user_id = str(user_id) if user_id else str(current_user["id"])
    query = query.eq("user_id", target_user_id)
    if quiz_id:
        query = query.eq("quiz_id", str(quiz_id))
    query = query.order("started_at", desc=True)
    res = query.execute()
    attempts = res.data or []

    # Enrich with quiz titles & languages
    quiz_ids = list({str(a["quiz_id"]) for a in attempts if a.get("quiz_id")})
    quizzes_map = {}
    if quiz_ids:
        q_res = (
            db.table("quizzes")
            .select("id, title, language, topic")
            .in_("id", quiz_ids)
            .execute()
        )
        for q in q_res.data or []:
            quizzes_map[str(q["id"])] = q

    for att in attempts:
        q = quizzes_map.get(str(att.get("quiz_id")), {})
        att["quiz_title"] = q.get("title") or "Language Quiz"
        att["language"] = q.get("language") or "Spanish"
        if "exercise_attempts" not in att:
            att["exercise_attempts"] = []

    return attempts


@router.get("/{attempt_id}", response_model=QuizAttemptResponse)
async def get_quiz_attempt(
    attempt_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("quiz_attempts").select("*").eq("id", str(attempt_id)).execute()
    if not res.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz attempt not found"
        )
    attempt = res.data[0]

    # Fetch quiz details
    if attempt.get("quiz_id"):
        q_res = (
            db.table("quizzes")
            .select("id, title, language, topic")
            .eq("id", str(attempt["quiz_id"]))
            .execute()
        )
        if q_res.data:
            attempt["quiz_title"] = q_res.data[0].get("title")
            attempt["language"] = q_res.data[0].get("language")

    # Fetch associated exercise attempts
    ex_res = (
        db.table("exercise_attempts")
        .select("*")
        .eq("quiz_attempt_id", str(attempt_id))
        .order("created_at")
        .execute()
    )
    exercise_attempts = ex_res.data or []

    # Enrich exercise attempts with exercise questions, answers, and explanations
    ex_ids = list(
        {str(ea["exercise_id"]) for ea in exercise_attempts if ea.get("exercise_id")}
    )
    exercises_map = {}
    if ex_ids:
        raw_exercises = (
            db.table("exercises").select("*").in_("id", ex_ids).execute().data or []
        )
        for raw in raw_exercises:
            exercises_map[str(raw["id"])] = raw

    for ea in exercise_attempts:
        raw = exercises_map.get(str(ea.get("exercise_id")), {})
        payload = raw.get("payload", {})
        ea["prompt"] = raw.get("prompt") or "Exercise Question"
        ea["explanation"] = (
            payload.get("explanation") or "Focus on grammar and vocabulary rules."
        )

        correct_ans = payload.get("correct_answer")
        if not correct_ans and payload.get("correct_order"):
            correct_ans = " ".join(payload.get("correct_order"))
        elif not correct_ans and payload.get("pairs"):
            correct_ans = ", ".join(
                f"{p['left']} = {p['right']}" for p in payload["pairs"]
            )
        ea["correct_answer"] = correct_ans or ""
        ea["concept"] = raw.get("prompt") or "Grammar & Vocabulary"

    attempt["exercise_attempts"] = exercise_attempts
    return attempt


@router.post(
    "", response_model=QuizAttemptResponse, status_code=status.HTTP_201_CREATED
)
async def create_quiz_attempt(
    attempt_in: QuizAttemptCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_supabase),
):
    payload = attempt_in.model_dump(mode="json")
    mistakes = payload.pop("mistakes", None)
    answers = payload.pop("answers", None)
    payload.pop("time_spent_seconds", None)

    if not payload.get("user_id"):
        payload["user_id"] = str(current_user["id"])
    if not payload.get("completed_at"):
        payload["completed_at"] = datetime.now(UTC).isoformat()

    res = db.table("quiz_attempts").insert(payload).execute()
    if not res.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create quiz attempt",
        )
    attempt = res.data[0]
    attempt_id = attempt["id"]

    # Record all exercise attempts or mistakes into exercise_attempts table
    exercise_attempts = []
    items_to_record = []
    if answers and isinstance(answers, list):
        items_to_record = answers
    elif mistakes and isinstance(mistakes, list):
        items_to_record = mistakes

    for item in items_to_record:
        ex_id = item.get("exerciseId") or item.get("exercise_id")
        if ex_id:
            user_ans = str(
                item.get("userAnswer")
                or item.get("user_answer")
                or item.get("answer")
                or ""
            )
            is_corr = (
                item.get("isCorrect")
                if "isCorrect" in item
                else item.get("is_correct", False)
            )
            try:
                ea_res = (
                    db.table("exercise_attempts")
                    .insert(
                        {
                            "quiz_attempt_id": str(attempt_id),
                            "exercise_id": str(ex_id),
                            "answer": user_ans,
                            "is_correct": bool(is_corr),
                        }
                    )
                    .execute()
                )
                if ea_res.data:
                    exercise_attempts.append(ea_res.data[0])
            except Exception:
                pass

    attempt["exercise_attempts"] = exercise_attempts
    return attempt


@router.put("/{attempt_id}", response_model=QuizAttemptResponse)
async def update_quiz_attempt(
    attempt_id: UUID,
    attempt_in: QuizAttemptUpdate,
    db: Client = Depends(get_supabase),
):
    payload = attempt_in.model_dump(exclude_unset=True, mode="json")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )
    res = db.table("quiz_attempts").update(payload).eq("id", str(attempt_id)).execute()
    if not res.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz attempt not found or update failed",
        )
    attempt = res.data[0]

    ex_res = (
        db.table("exercise_attempts")
        .select("*")
        .eq("quiz_attempt_id", str(attempt_id))
        .execute()
    )
    attempt["exercise_attempts"] = ex_res.data or []
    return attempt


@router.delete("/{attempt_id}")
async def delete_quiz_attempt(
    attempt_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("quiz_attempts").delete().eq("id", str(attempt_id)).execute()
    if not res.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz attempt not found or delete failed",
        )
    return {"message": "Quiz attempt deleted successfully", "id": str(attempt_id)}
