import json
import logging
import os
import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from supabase import Client

from apps.api.core.config import settings
from apps.api.core.db import get_supabase
from apps.api.schemas.generation import GeneratedQuizContent

logger = logging.getLogger(__name__)


class QuizGenerationService:
    def __init__(self, db: Optional[Client] = None):
        self.db = db or get_supabase()
        self.api_key = (
            settings.GEMINI_API_KEY
            or settings.GOOGLE_API_KEY
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
        )
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Google GenAI client initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Google GenAI Client: {e}")

    def is_ai_available(self) -> bool:
        return self.client is not None

    async def generate_with_gemini(
        self, language: str, level: str, topic: str, count: int
    ) -> Optional[GeneratedQuizContent]:
        """Generate structured quiz content using the Google GenAI SDK."""
        if not self.client:
            return None

        from google.genai import types

        prompt = f"""
You are an expert language instructor and curriculum designer.
Create a high-quality, pedagogically sound quiz for language learners.

Specifications:
- Target Language: {language}
- CEFR Proficiency Level: {level}
- Quiz Topic / Context: {topic}
- Target Question Count: {count}

Generate a comprehensive set of exercises adhering to the provided JSON schema:
1. multiple_choice_exercises: Practical translation or phrase completion questions with 3 to 4 distinct options and one clear correct answer.
2. fill_in_blank_exercises: Meaningful sentences with '_____' where the missing word should go, along with the exact correct answer and a helpful hint.
3. word_order_exercises: Scrambled sentence puzzles with the words in correct order, plus 1 or 2 extra plausible distractor words.
4. matching_exercises: Vocabulary pairs matching English/source words to their {language} equivalents.

Ensure vocabulary and grammatical constructs are appropriate for {level} level learners.
"""

        try:
            model_name = settings.GEMINI_MODEL or "gemini-2.5-flash"
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=GeneratedQuizContent,
                    temperature=0.7,
                ),
            )

            if response and response.text:
                return GeneratedQuizContent.model_validate_json(response.text)
        except Exception as exc:
            logger.warning(f"Google GenAI SDK call failed: {exc}. Falling back to dynamic curriculum builder.")

        return None

    def generate_fallback_content(
        self, language: str, level: str, topic: str, count: int
    ) -> GeneratedQuizContent:
        """Generate deterministic, high-quality contextual exercises when GenAI is unavailable or rate-limited."""
        lang = language.capitalize()
        t = topic.lower()

        title = f"{topic} Essentials"
        description = f"Interactive {lang} practice focusing on essential {topic.lower()} expressions and sentence mechanics."

        if "coffee" in t or "cafe" in t:
            mcq_prompt = f"How do you order a coffee in {lang}?"
            mcq_options = ["Un café, por favor.", "Una cerveza, gracias.", "Una manzana, por favor."] if lang == "Spanish" else [
                "Un café, s'il vous plaît.", "Une bière, merci.", "Une pomme, s'il vous plaît."
            ]
            fib_prompt = "Complete the phrase: \"Una mesa para dos, por _____\"" if lang == "Spanish" else "Complete the phrase: \"Une table pour deux, s'il vous _____\""
            fib_answer = "favor" if lang == "Spanish" else "plaît"
            fib_hint = f"{lang} for 'please'"

            wo_prompt = "Arrange the sentence: 'The check, please.'"
            wo_order = ["La", "cuenta", "por", "favor"] if lang == "Spanish" else ["L'addition", "s'il", "vous", "plaît"]
            wo_distractors = ["el", "menú"] if lang == "Spanish" else ["le", "menu"]

            pairs = [
                {"left": "Coffee", "right": "El café" if lang == "Spanish" else "Le café"},
                {"left": "Bill / Check", "right": "La cuenta" if lang == "Spanish" else "L'addition"},
                {"left": "Water", "right": "El agua" if lang == "Spanish" else "L'eau"},
                {"left": "Menu", "right": "El menú" if lang == "Spanish" else "Le menu"},
            ]
        elif "food" in t or "din" in t or "restaurant" in t:
            mcq_prompt = f"How do you say 'I want to order food' in {lang}?"
            mcq_options = ["Quiero ordenar la comida.", "Voy a dormir ahora.", "Me gusta el carro."] if lang == "Spanish" else [
                "Je voudrais commander.", "Je vais dormir.", "J'aime la voiture."
            ]
            fib_prompt = "Complete the phrase: \"El plato del _____ (day)\"" if lang == "Spanish" else "Complete the phrase: \"Le plat du _____ (day)\""
            fib_answer = "día" if lang == "Spanish" else "jour"
            fib_hint = "Word for 'day'"

            wo_prompt = "Arrange the sentence: 'The food is very delicious.'"
            wo_order = ["La", "comida", "está", "muy", "deliciosa"] if lang == "Spanish" else ["La", "nourriture", "est", "très", "délicieuse"]
            wo_distractors = ["ayer"] if lang == "Spanish" else ["hier"]

            pairs = [
                {"left": "Bread", "right": "El pan" if lang == "Spanish" else "Le pain"},
                {"left": "Delicious", "right": "Delicioso" if lang == "Spanish" else "Délicieux"},
                {"left": "Table", "right": "La mesa" if lang == "Spanish" else "La table"},
                {"left": "Glass", "right": "El vaso" if lang == "Spanish" else "Le verre"},
            ]
        elif "travel" in t or "direction" in t:
            mcq_prompt = f"How do you ask 'Where is the train station?' in {lang}?"
            mcq_options = ["¿Dónde está la estación de tren?", "¿Cuándo comemos hoy?", "¿Cómo te llamas?"] if lang == "Spanish" else [
                "Où est la gare?", "Quand mangeons-nous?", "Comment vous appelez-vous?"
            ]
            fib_prompt = "Complete the phrase: \"Gire a la _____ (right)\"" if lang == "Spanish" else "Complete the phrase: \"Tournez à _____ (right)\""
            fib_answer = "derecha" if lang == "Spanish" else "droite"
            fib_hint = "Direction opposite of left"

            wo_prompt = "Arrange the sentence: 'A ticket to Madrid, please.'" if lang == "Spanish" else "Arrange the sentence: 'A ticket to Paris, please.'"
            wo_order = ["Un", "billete", "para", "Madrid", "por", "favor"] if lang == "Spanish" else ["Un", "billet", "pour", "Paris", "s'il", "vous", "plaît"]
            wo_distractors = ["el", "tren"] if lang == "Spanish" else ["le", "train"]

            pairs = [
                {"left": "Airport", "right": "El aeropuerto" if lang == "Spanish" else "L'aéroport"},
                {"left": "Train", "right": "El tren" if lang == "Spanish" else "Le train"},
                {"left": "Ticket", "right": "El billete" if lang == "Spanish" else "Le billet"},
                {"left": "Hotel", "right": "El hotel" if lang == "Spanish" else "L'hôtel"},
            ]
        else:
            mcq_prompt = f"How do you say 'Good morning, how are you?' in {lang}?"
            mcq_options = ["Buenos días, ¿cómo estás?", "Buenas noches, adiós.", "Hasta luego, gracias."] if lang == "Spanish" else [
                "Bonjour, comment allez-vous?", "Bonne nuit, au revoir.", "À bientôt, merci."
            ]
            fib_prompt = "Complete the phrase: \"Mucho _____ (nice to meet you)\"" if lang == "Spanish" else "Complete the phrase: \"Enchanté de faire votre _____\""
            fib_answer = "gusto" if lang == "Spanish" else "connaissance"
            fib_hint = "Polite social expression"

            wo_prompt = f"Arrange the sentence: 'I speak a little {lang}.'"
            wo_order = ["Hablo", "un", "poco", "de", "español"] if lang == "Spanish" else ["Je", "parle", "un", "peu", "français"]
            wo_distractors = ["mucho"] if lang == "Spanish" else ["beaucoup"]

            pairs = [
                {"left": "Friend", "right": "El amigo" if lang == "Spanish" else "L'ami"},
                {"left": "House", "right": "La casa" if lang == "Spanish" else "La maison"},
                {"left": "Today", "right": "Hoy" if lang == "Spanish" else "Aujourd'hui"},
                {"left": "Thank you", "right": "Gracias" if lang == "Spanish" else "Merci"},
            ]

        from apps.api.schemas.generation import (
            GeneratedFillInBlank,
            GeneratedMatching,
            GeneratedMatchingPair,
            GeneratedMultipleChoice,
            GeneratedWordOrder,
        )

        return GeneratedQuizContent(
            title=title,
            description=description,
            multiple_choice_exercises=[
                GeneratedMultipleChoice(
                    prompt=mcq_prompt,
                    options=mcq_options,
                    correct_answer=mcq_options[0],
                )
            ],
            fill_in_blank_exercises=[
                GeneratedFillInBlank(
                    prompt=fib_prompt,
                    correct_answer=fib_answer,
                    hint=fib_hint,
                )
            ],
            word_order_exercises=[
                GeneratedWordOrder(
                    prompt=wo_prompt,
                    correct_order=wo_order,
                    distractors=wo_distractors,
                )
            ],
            matching_exercises=[
                GeneratedMatching(
                    prompt=f"Match {lang} vocabulary terms:",
                    pairs=[GeneratedMatchingPair(**p) for p in pairs],
                )
            ],
        )

    def _convert_to_exercise_records(
        self, content: GeneratedQuizContent, quiz_id: str, count: int = 4
    ) -> List[Dict[str, Any]]:
        """Transforms GeneratedQuizContent into database exercise row payloads."""
        exercises = []
        pos = 1

        # 1. Multiple Choice
        for mcq in content.multiple_choice_exercises:
            if pos > count:
                break
            opts = list(mcq.options)
            if mcq.correct_answer not in opts:
                opts.append(mcq.correct_answer)
            random.shuffle(opts)

            exercises.append({
                "quiz_id": quiz_id,
                "type": "multiple_choice",
                "position": pos,
                "prompt": mcq.prompt,
                "payload": {
                    "options": opts,
                    "correct_answer": mcq.correct_answer,
                },
            })
            pos += 1

        # 2. Fill in Blank
        for fib in content.fill_in_blank_exercises:
            if pos > count:
                break
            exercises.append({
                "quiz_id": quiz_id,
                "type": "fill_in_blank",
                "position": pos,
                "prompt": fib.prompt,
                "payload": {
                    "correct_answer": fib.correct_answer,
                    "hint": fib.hint,
                },
            })
            pos += 1

        # 3. Word Order
        for wo in content.word_order_exercises:
            if pos > count:
                break
            tokens = list(wo.correct_order)
            if wo.distractors:
                tokens.extend(wo.distractors)
            random.shuffle(tokens)

            exercises.append({
                "quiz_id": quiz_id,
                "type": "word_order",
                "position": pos,
                "prompt": wo.prompt,
                "payload": {
                    "tokens": tokens,
                    "correct_order": wo.correct_order,
                },
            })
            pos += 1

        # 4. Matching
        for match in content.matching_exercises:
            if pos > count:
                break
            exercises.append({
                "quiz_id": quiz_id,
                "type": "matching",
                "position": pos,
                "prompt": match.prompt,
                "payload": {
                    "pairs": [p.model_dump() for p in match.pairs],
                },
            })
            pos += 1

        return exercises

    async def execute_job(
        self, job_id: str, language: str, level: str, topic: str, count: int = 4
    ) -> Optional[str]:
        """Executes full quiz generation lifecycle and records result in database."""
        try:
            # 1. Update job to in_progress
            now_iso = datetime.now(timezone.utc).isoformat()
            self.db.table("generation_jobs").update({
                "status": "in_progress",
                "started_at": now_iso,
            }).eq("id", job_id).execute()

            # 2. Generate content (try Google GenAI SDK first)
            content = None
            if self.is_ai_available():
                logger.info(f"Generating quiz with Google GenAI SDK for topic='{topic}', lang='{language}'...")
                content = await self.generate_with_gemini(language, level, topic, count)

            if not content:
                logger.info("Using dynamic curriculum engine for quiz generation...")
                content = self.generate_fallback_content(language, level, topic, count)

            # 3. Insert Quiz record
            quiz_insert = self.db.table("quizzes").insert({
                "title": content.title or f"{topic} Essentials",
                "topic": topic,
                "language": language,
                "level": level,
            }).execute()

            if not quiz_insert.data:
                raise Exception("Failed to insert generated quiz into database")

            quiz_id = str(quiz_insert.data[0]["id"])

            # 4. Insert Exercises
            exercise_records = self._convert_to_exercise_records(content, quiz_id, count)
            for ex in exercise_records:
                self.db.table("exercises").insert(ex).execute()

            # 5. Mark job completed
            completed_iso = datetime.now(timezone.utc).isoformat()
            self.db.table("generation_jobs").update({
                "status": "completed",
                "quiz_id": quiz_id,
                "completed_at": completed_iso,
            }).eq("id", job_id).execute()

            logger.info(f"Quiz generation job {job_id} succeeded with quiz {quiz_id}")
            return quiz_id

        except Exception as exc:
            logger.exception(f"Quiz generation job {job_id} failed: {exc}")
            self.db.table("generation_jobs").update({
                "status": "failed",
                "error": str(exc),
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }).eq("id", job_id).execute()
            return None
