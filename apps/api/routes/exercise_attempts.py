from typing import List, Optional, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from apps.api.core.db import get_supabase
from apps.api.core.auth import get_current_user
from apps.api.schemas.exercise_attempt import (
    ExerciseAttemptCreate,
    ExerciseAttemptResponse,
    ExerciseAttemptUpdate,
)

router = APIRouter(prefix="/exercise-attempts", tags=["exercise-attempts"], dependencies=[Depends(get_current_user)])


from pydantic import BaseModel

class CheckAnswerRequest(BaseModel):
    quiz_id: UUID
    exercise_id: UUID
    user_answer: Any

class CheckAnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: str
    xp_earned: int

@router.post("/check", response_model=CheckAnswerResponse)
async def check_exercise_answer(
    request: CheckAnswerRequest,
    db: Client = Depends(get_supabase),
):
    # Fetch the exercise to get the correct answer
    res = db.table("exercises").select("*").eq("id", str(request.exercise_id)).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    exercise = res.data[0]
    ex_type = exercise["type"]
    payload = exercise["payload"]
    
    is_correct = False
    correct_answer = ""
    
    # Evaluate based on exercise type
    if ex_type == "multiple_choice":
        correct_answer = payload.get("correct_answer", "")
        is_correct = str(request.user_answer).strip() == str(correct_answer).strip()
        explanation = payload.get("explanation") or (
            "Great job! Accurate translation." if is_correct else f"The correct answer is '{correct_answer}'."
        )
    elif ex_type == "fill_in_blank":
        correct_answer = payload.get("correct_answer", "")
        is_correct = str(request.user_answer).lower().strip() == str(correct_answer).lower().strip()
        explanation = payload.get("explanation") or (
            "Perfect! You filled in the exact grammatical form." if is_correct else f"Expected '{correct_answer}'."
        )
    elif ex_type == "word_order":
        correct_answer_list = payload.get("correct_order", [])
        correct_answer = " ".join(correct_answer_list)
        if isinstance(request.user_answer, list):
            is_correct = request.user_answer == correct_answer_list
        else:
            is_correct = str(request.user_answer).strip() == correct_answer.strip()
        explanation = payload.get("explanation") or (
            "Well done! Natural word order." if is_correct else f"Correct sequence: {correct_answer}"
        )
    elif ex_type == "matching":
        pairs = payload.get("pairs", [])
        # pairs is [{'left': 'Coffee', 'right': 'El café'}, ...]
        # user_answer is {'p0': 'El café', ...} or similar dict
        pair_dict = {p.get("left"): p.get("right") for p in pairs if isinstance(p, dict)}
        if isinstance(request.user_answer, dict) and request.user_answer:
            # Check matches
            all_match = True
            for k, v in request.user_answer.items():
                expected = pair_dict.get(k)
                if expected and expected != v:
                    all_match = False
            is_correct = all_match
        else:
            is_correct = True
        correct_answer = ", ".join(f"{p.get('left')} = {p.get('right')}" for p in pairs if isinstance(p, dict))
        explanation = "All terms matched correctly!" if is_correct else "Review the vocabulary pairings."
    else:
        is_correct = True
        correct_answer = str(request.user_answer)
        explanation = "Good effort!"

    return CheckAnswerResponse(
        is_correct=is_correct,
        correct_answer=correct_answer,
        explanation=explanation,
        xp_earned=10 if is_correct else 0
    )

@router.get("", response_model=List[ExerciseAttemptResponse])
async def get_exercise_attempts(
    quiz_attempt_id: Optional[UUID] = None,
    exercise_id: Optional[UUID] = None,
    db: Client = Depends(get_supabase),
):
    query = db.table("exercise_attempts").select("*")
    if quiz_attempt_id:
        query = query.eq("quiz_attempt_id", str(quiz_attempt_id))
    if exercise_id:
        query = query.eq("exercise_id", str(exercise_id))
    res = query.execute()
    return res.data or []


@router.get("/{attempt_id}", response_model=ExerciseAttemptResponse)
async def get_exercise_attempt(
    attempt_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("exercise_attempts").select("*").eq("id", str(attempt_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise attempt not found")
    return res.data[0]


@router.post("", response_model=ExerciseAttemptResponse, status_code=status.HTTP_201_CREATED)
async def create_exercise_attempt(
    attempt_in: ExerciseAttemptCreate,
    db: Client = Depends(get_supabase),
):
    payload = attempt_in.model_dump(mode="json")
    res = db.table("exercise_attempts").insert(payload).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create exercise attempt")
    return res.data[0]


@router.put("/{attempt_id}", response_model=ExerciseAttemptResponse)
async def update_exercise_attempt(
    attempt_id: UUID,
    attempt_in: ExerciseAttemptUpdate,
    db: Client = Depends(get_supabase),
):
    payload = attempt_in.model_dump(exclude_unset=True, mode="json")
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")
    res = db.table("exercise_attempts").update(payload).eq("id", str(attempt_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise attempt not found or update failed")
    return res.data[0]


@router.delete("/{attempt_id}")
async def delete_exercise_attempt(
    attempt_id: UUID,
    db: Client = Depends(get_supabase),
):
    res = db.table("exercise_attempts").delete().eq("id", str(attempt_id)).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise attempt not found or delete failed")
    return {"message": "Exercise attempt deleted successfully", "id": str(attempt_id)}
