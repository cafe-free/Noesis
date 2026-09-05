from uuid import UUID
from typing import List
from apps.api.db.supabase import get_supabase
from apps.api.schemas.attempt import AnswerSubmissionRequest, AnswerSubmissionResponse, ExerciseResult
from fastapi import HTTPException

class QuizService:
    def __init__(self):
        self.supabase = get_supabase()

    def evaluate_attempt(self, attempt: AnswerSubmissionRequest) -> AnswerSubmissionResponse:
        # Get exercises to validate answers
        ex_res = self.supabase.table("exercises").select("*").eq("quiz_id", str(attempt.quiz_id)).execute()
        if not ex_res.data:
            raise HTTPException(status_code=404, detail="Quiz not found or has no exercises")
            
        exercises_dict = {ex["id"]: ex for ex in ex_res.data}
        
        # Create attempt
        attempt_res = self.supabase.table("quiz_attempts").insert({
            "user_id": str(attempt.user_id),
            "quiz_id": str(attempt.quiz_id),
            "total_questions": len(exercises_dict)
        }).execute()
        
        attempt_id = attempt_res.data[0]["id"]
        
        results: List[ExerciseResult] = []
        correct_count = 0
        
        ex_attempts_to_insert = []
        
        for ans in attempt.answers:
            ex_id_str = str(ans.exercise_id)
            if ex_id_str not in exercises_dict:
                continue
                
            ex = exercises_dict[ex_id_str]
            payload = ex["payload"]
            is_correct = False
            
            # Simple evaluation logic
            if ex["type"] == "mcq_translation":
                is_correct = ans.answer == payload.get("correct_answer")
            elif ex["type"] == "fill_blank":
                is_correct = ans.answer == payload.get("correct_answer") or ans.answer in payload.get("acceptable_answers", [])
            elif ex["type"] == "word_order":
                is_correct = ans.answer == payload.get("correct_order")
            elif ex["type"] == "matching":
                # Assuming ans.answer is a dict {left: right}
                pass # more complex validation omitted for brevity
                
            if is_correct:
                correct_count += 1
                
            results.append(ExerciseResult(exercise_id=ans.exercise_id, is_correct=is_correct))
            
            ex_attempts_to_insert.append({
                "quiz_attempt_id": attempt_id,
                "exercise_id": ex_id_str,
                "answer": str(ans.answer),
                "is_correct": is_correct,
                "response_time_ms": ans.response_time_ms
            })
            
        # Bulk insert exercise attempts
        if ex_attempts_to_insert:
            self.supabase.table("exercise_attempts").insert(ex_attempts_to_insert).execute()
            
        score = (correct_count / len(exercises_dict)) * 100 if exercises_dict else 0
        
        # Update quiz attempt
        self.supabase.table("quiz_attempts").update({
            "score": score,
            "correct_answers": correct_count,
            "completed_at": attempt_res.data[0]["started_at"] # just for simplicity, usually current time
        }).eq("id", attempt_id).execute()
        
        return AnswerSubmissionResponse(
            attempt_id=UUID(attempt_id),
            score=score,
            correct_answers=correct_count,
            total_questions=len(exercises_dict),
            results=results
        )
