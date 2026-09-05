import asyncio
from uuid import UUID
from datetime import datetime
import logging
from apps.api.db.supabase import get_supabase
from apps.api.agents.base import GeminiProvider
from apps.api.agents.curriculum import CurriculumAgent
from apps.api.agents.exercise import ExerciseAgent
from apps.api.agents.distractor import DistractorAgent
from apps.api.agents.qa import QAAgent
import random

logger = logging.getLogger(__name__)

class GenerationService:
    def __init__(self, provider=None):
        self.provider = provider or GeminiProvider()
        self.supabase = get_supabase()
        self.curriculum_agent = CurriculumAgent(self.provider)
        self.exercise_agent = ExerciseAgent(self.provider)
        self.distractor_agent = DistractorAgent(self.provider)
        self.qa_agent = QAAgent(self.provider)

    async def run_generation_job(self, job_id: str):
        try:
            # Update status to running
            self.supabase.table("generation_jobs").update({
                "status": "running",
                "started_at": datetime.utcnow().isoformat()
            }).eq("id", job_id).execute()

            # Get job details
            job_res = self.supabase.table("generation_jobs").select("*").eq("id", job_id).execute()
            if not job_res.data:
                raise Exception(f"Job {job_id} not found")
            job = job_res.data[0]

            language = job["language"]
            level = job["level"]
            topic = job["topic"]
            count = job["count"]

            logger.info(f"Generating curriculum for job {job_id}")
            curriculum = await self.curriculum_agent.generate_curriculum(language, level, topic)

            logger.info(f"Generating exercises for job {job_id}")
            raw_exercises = await self.exercise_agent.generate_exercises(language, level, topic, curriculum, count)

            valid_exercises = []
            for raw_ex in raw_exercises:
                # Add distractors
                payload = await self.distractor_agent.generate_distractors(language, level, raw_ex["type"], raw_ex["payload"])
                raw_ex["payload"] = payload
                
                # Word order tokens fix
                if raw_ex["type"] == "word_order" and not raw_ex["payload"].get("tokens"):
                    tokens = list(raw_ex["payload"].get("correct_order", []))
                    random.shuffle(tokens)
                    raw_ex["payload"]["tokens"] = tokens

                # QA Validation
                qa_res = await self.qa_agent.validate_exercise(language, level, raw_ex)
                if qa_res.valid:
                    valid_exercises.append(raw_ex)
                else:
                    logger.warning(f"Exercise failed QA: {qa_res.issues}")

            # Save to database
            # 1. Create Lesson (optional, but let's create a stub)
            lesson_res = self.supabase.table("lessons").insert({
                "language": language,
                "level": level,
                "topic": topic,
                "title": f"{language} {level}: {topic}"
            }).execute()
            lesson_id = lesson_res.data[0]["id"]

            # 2. Create Quiz
            quiz_res = self.supabase.table("quizzes").insert({
                "lesson_id": lesson_id,
                "language": language,
                "level": level,
                "topic": topic,
                "title": f"Quiz on {topic}"
            }).execute()
            quiz_id = quiz_res.data[0]["id"]

            # 3. Save Exercises
            exercises_to_insert = []
            for i, ex in enumerate(valid_exercises):
                exercises_to_insert.append({
                    "quiz_id": quiz_id,
                    "type": ex["type"],
                    "position": i + 1,
                    "prompt": ex["prompt"],
                    "payload": ex["payload"]
                })
            
            if exercises_to_insert:
                self.supabase.table("exercises").insert(exercises_to_insert).execute()

            # Update job completed
            self.supabase.table("generation_jobs").update({
                "status": "completed",
                "quiz_id": quiz_id,
                "completed_at": datetime.utcnow().isoformat()
            }).eq("id", job_id).execute()
            
            logger.info(f"Job {job_id} completed successfully")

        except Exception as e:
            logger.exception(f"Job {job_id} failed")
            self.supabase.table("generation_jobs").update({
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat()
            }).eq("id", job_id).execute()
