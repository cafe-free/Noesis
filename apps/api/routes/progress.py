from datetime import datetime, timezone
from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from supabase import Client

from apps.api.core.auth import get_current_user
from apps.api.core.db import get_supabase
from apps.api.schemas.progress import ProgressResponse, WeakAreaItemResponse

router = APIRouter(prefix="/progress", tags=["progress"], dependencies=[Depends(get_current_user)])


@router.get("/me", response_model=ProgressResponse)
async def get_my_progress(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_supabase),
):
    user_id = str(current_user["id"])
    attempts_res = db.table("quiz_attempts").select("*").eq("user_id", user_id).execute()
    attempts = attempts_res.data or []

    total_correct = sum(int(a.get("correct_answers") or 0) for a in attempts)
    total_xp = total_correct * 10

    # Calculate today's XP
    now_utc = datetime.now(timezone.utc)
    today_date = now_utc.date()
    today_xp = 0
    for a in attempts:
        comp_str = a.get("completed_at")
        if comp_str:
            try:
                comp_dt = datetime.fromisoformat(comp_str.replace("Z", "+00:00"))
                if comp_dt.date() == today_date:
                    today_xp += int(a.get("correct_answers") or 0) * 10
            except Exception:
                pass

    streak_days = max(1, len({a.get("completed_at", "")[:10] for a in attempts if a.get("completed_at")}))

    name = current_user.get("username") or current_user.get("email", "").split("@")[0] or "Learner"

    return ProgressResponse(
        id=current_user["id"],
        name=name,
        email=current_user["email"],
        learningLanguage="Spanish",
        nativeLanguage="English",
        currentLevel="A1",
        streakDays=streak_days,
        totalXp=total_xp,
        dailyGoalXp=50,
        todayXp=today_xp,
        hearts=5,
        maxHearts=5,
    )


@router.get("/me/weaknesses", response_model=List[WeakAreaItemResponse])
async def get_my_weaknesses(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Client = Depends(get_supabase),
):
    user_id = str(current_user["id"])
    # Fetch user's quiz attempts
    attempts_res = db.table("quiz_attempts").select("id, quiz_id").eq("user_id", user_id).execute()
    attempts = attempts_res.data or []

    if not attempts:
        return []

    attempt_ids = [str(a["id"]) for a in attempts]
    
    # Query exercise attempts that were incorrect
    ea_query = db.table("exercise_attempts").select("*").in_("quiz_attempt_id", attempt_ids).eq("is_correct", False).execute()
    mistakes = ea_query.data or []

    if not mistakes:
        return []

    # Map exercise_id to mistakes
    ex_ids = list({str(m["exercise_id"]) for m in mistakes if m.get("exercise_id")})
    exercises_map = {}
    if ex_ids:
        ex_res = db.table("exercises").select("id, prompt, quiz_id").in_("id", ex_ids).execute()
        for ex in ex_res.data or []:
            exercises_map[str(ex["id"])] = ex

    quizzes_map = {}
    quiz_ids = list({str(ex["quiz_id"]) for ex in exercises_map.values() if ex.get("quiz_id")})
    if quiz_ids:
        q_res = db.table("quizzes").select("id, topic").in_("id", quiz_ids).execute()
        for q in q_res.data or []:
            quizzes_map[str(q["id"])] = q.get("topic", "Grammar")

    result: List[WeakAreaItemResponse] = []
    for m in mistakes[:5]:
        ex_id = str(m.get("exercise_id"))
        ex = exercises_map.get(ex_id, {})
        topic = quizzes_map.get(str(ex.get("quiz_id")), "General Practice")
        concept = ex.get("prompt") or "Vocabulary & Word Choice"

        result.append(
            WeakAreaItemResponse(
                id=str(m["id"]),
                topic=topic,
                concept=concept,
                accuracyRate=50,
                mistakeCount=1,
                lastPracticed="Recent",
            )
        )

    return result
