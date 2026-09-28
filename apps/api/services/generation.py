import logging
import os
import random
from datetime import UTC, datetime
from typing import Any

from supabase import Client

from apps.api.core.config import settings
from apps.api.core.db import get_supabase
from apps.api.schemas.generation import (
    GeneratedFillInBlank,
    GeneratedMatching,
    GeneratedMatchingPair,
    GeneratedMultipleChoice,
    GeneratedQuizContent,
    GeneratedWordOrder,
)

logger = logging.getLogger(__name__)


class QuizGenerationService:
    def __init__(self, db: Client | None = None):
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
    ) -> GeneratedQuizContent | None:
        """Generate structured quiz content using the Google GenAI SDK with Gemma 4."""
        if not self.client:
            return None

        from google.genai import types

        prompt = f"""You are an expert language teacher and quiz generator.
Your task is to generate an interactive quiz for students learning {language.upper()}.

CRITICAL LANGUAGE ENFORCEMENT:
- The target language is EXCLUSIVELY: {language.upper()}
- All target phrases, vocabulary choices, sentence puzzle tokens, and correct answers MUST be written in {language.upper()}.
- ABSOLUTELY DO NOT generate French, Spanish, or any other language unless {language.upper()} is specifically that language.
- For Japanese: You MUST use authentic Japanese (Kanji/Hiragana/Katakana with Romaji where helpful). Never output French or Spanish.
- For German: Use German. For Italian: Use Italian. For Spanish: Use Spanish. For French: Use French.
- CEFR Level: {level}
- Topic/Context: {topic}
- Target question count: {count}

SCHEMA REQUIREMENTS:
1. multiple_choice_exercises:
   - "prompt": English prompt asking for the translation or phrase in {language} (e.g., "How do you say 'A coffee, please' in {language}?")
   - "options": 3 to 4 distinct choices written entirely in {language}.
   - "correct_answer": Exactly one of the options, written in {language}.

2. fill_in_blank_exercises:
   - "prompt": A sentence in {language} with '_____' marking the missing word, followed by the English translation in parentheses.
   - "correct_answer": The exact missing word in {language}.
   - "hint": A concise hint in English.

3. word_order_exercises:
   - "prompt": "Arrange the sentence: '<English meaning>'"
   - "correct_order": List of words/tokens in {language} in grammatical sequence.
   - "distractors": 1 or 2 extra plausible words in {language}.

4. matching_exercises:
   - "prompt": "Match the vocabulary terms in {language}:"
   - "pairs": 3 to 4 pairs where "left" is the English term and "right" is the translation in {language}.

5. "title": A descriptive title in English (e.g., "{topic} in {language}").
6. "description": A 1-2 sentence description of learning outcomes in {language}.

REMINDER: Output ONLY {language.upper()} for all target expressions, choices, and answers.
"""

        # Model identifier configured to gemma-4
        preferred_model = settings.GEMINI_MODEL or "gemma-4"
        candidate_models = [preferred_model]
        if preferred_model != "gemma-4":
            candidate_models.append("gemma-4")
        if "gemini-2.5-flash" not in candidate_models:
            candidate_models.append("gemini-2.5-flash")

        for model_name in candidate_models:
            try:
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
                    parsed = GeneratedQuizContent.model_validate_json(response.text)
                    logger.info(
                        f"Successfully generated quiz content using model '{model_name}'."
                    )
                    return parsed
            except Exception as exc:
                logger.warning(f"Generation with model '{model_name}' failed: {exc}")

        logger.warning(
            "All GenAI model attempts exhausted. Falling back to dynamic curriculum builder."
        )
        return None

    def generate_fallback_content(
        self, language: str, level: str, topic: str, count: int
    ) -> GeneratedQuizContent:
        """Generate deterministic, high-quality contextual exercises in the exact target language."""
        lang = language.strip().capitalize()
        t = topic.lower()

        title = f"{topic} in {lang}"
        description = f"Interactive {lang} practice focusing on {topic.lower()} vocabulary and sentence patterns."

        # --- JAPANESE ---
        if lang == "Japanese":
            if "coffee" in t or "cafe" in t:
                mcq_prompt = "How do you order a coffee in Japanese?"
                mcq_options = [
                    "コーヒーをください (Koohii o kudasai)",
                    "お茶をください (Ocha o kudasai)",
                    "お水をください (Omizu o kudasai)",
                ]
                fib_prompt = 'Complete the phrase: "二人用のテーブルを_____ (A table for two, please)"'
                fib_answer = "お願いします"
                fib_hint = "Japanese for 'please / I request' (onegaishimasu)"
                wo_prompt = "Arrange the sentence: 'The check, please.'"
                wo_order = ["お会計を", "お願いします"]
                wo_distractors = ["メニューを", "水を"]
                pairs = [
                    {"left": "Coffee", "right": "コーヒー (Koohii)"},
                    {"left": "Bill / Check", "right": "お会計 (Okaikei)"},
                    {"left": "Water", "right": "お水 (Omizu)"},
                    {"left": "Menu", "right": "メニュー (Menyuu)"},
                ]
            elif "food" in t or "din" in t or "restaurant" in t:
                mcq_prompt = "How do you say 'This is delicious' in Japanese?"
                mcq_options = [
                    "これは美味しいです (Kore wa oishii desu)",
                    "これは高いです (Kore wa takai desu)",
                    "これは甘いです (Kore wa amai desu)",
                ]
                fib_prompt = 'Complete the phrase: "ごちそう_____でした (Thank you for the meal)"'
                fib_answer = "さま"
                fib_hint = "Honorific suffix in standard meal greeting (sama)"
                wo_prompt = "Arrange the sentence: 'I would like to order ramen.'"
                wo_order = ["ラーメンを", "注文したい", "です"]
                wo_distractors = ["昨日", "食べました"]
                pairs = [
                    {"left": "Delicious", "right": "美味しい (Oishii)"},
                    {"left": "Water", "right": "お水 (Omizu)"},
                    {"left": "Meal / Rice", "right": "ご飯 (Gohan)"},
                    {"left": "Table", "right": "テーブル (Teeburu)"},
                ]
            elif "travel" in t or "direction" in t:
                mcq_prompt = "How do you ask 'Where is the train station?' in Japanese?"
                mcq_options = [
                    "駅はどこですか？ (Eki wa doko desu ka?)",
                    "何時ですか？ (Nan-ji desu ka?)",
                    "トイレはどこですか？ (Toire wa doko desu ka?)",
                ]
                fib_prompt = 'Complete the phrase: "東京行きの切符を_____ (A ticket to Tokyo, please)"'
                fib_answer = "一枚ください"
                fib_hint = "Japanese for 'one ticket, please' (ichimai kudasai)"
                wo_prompt = "Arrange the sentence: 'Where is the station?'"
                wo_order = ["駅は", "どこ", "ですか"]
                wo_distractors = ["いつ", "誰"]
                pairs = [
                    {"left": "Station", "right": "駅 (Eki)"},
                    {"left": "Train", "right": "電車 (Densha)"},
                    {"left": "Ticket", "right": "切符 (Kippu)"},
                    {"left": "Airport", "right": "空港 (Kuukou)"},
                ]
            else:
                mcq_prompt = "How do you say 'Good morning' in Japanese?"
                mcq_options = [
                    "おはようございます (Ohayou gozaimasu)",
                    "こんにちは (Konnichiwa)",
                    "こんばんは (Konbanwa)",
                ]
                fib_prompt = 'Complete the phrase: "初めまして、どうぞよろしく_____ (Nice to meet you)"'
                fib_answer = "お願いします"
                fib_hint = "Japanese for 'please / I request' (onegaishimasu)"
                wo_prompt = "Arrange the sentence: 'I study Japanese every day.'"
                wo_order = ["私は", "毎日", "日本語を", "勉強します"]
                wo_distractors = ["英語", "とても"]
                pairs = [
                    {"left": "Thank you", "right": "ありがとう (Arigatou)"},
                    {"left": "Friend", "right": "友達 (Tomodachi)"},
                    {"left": "Today", "right": "今日 (Kyou)"},
                    {"left": "House", "right": "家 (Ie)"},
                ]

        # --- SPANISH ---
        elif lang == "Spanish":
            if "coffee" in t or "cafe" in t:
                mcq_prompt = "How do you order a coffee in Spanish?"
                mcq_options = [
                    "Un café, por favor.",
                    "Una cerveza, gracias.",
                    "Una manzana, por favor.",
                ]
                fib_prompt = 'Complete the phrase: "Una mesa para dos, por _____"'
                fib_answer = "favor"
                fib_hint = "Spanish for 'please'"
                wo_prompt = "Arrange the sentence: 'The check, please.'"
                wo_order = ["La", "cuenta", "por", "favor"]
                wo_distractors = ["el", "menú"]
                pairs = [
                    {"left": "Coffee", "right": "El café"},
                    {"left": "Bill / Check", "right": "La cuenta"},
                    {"left": "Water", "right": "El agua"},
                    {"left": "Menu", "right": "El menú"},
                ]
            elif "food" in t or "din" in t or "restaurant" in t:
                mcq_prompt = "How do you say 'I want to order food' in Spanish?"
                mcq_options = [
                    "Quiero ordenar la comida.",
                    "Voy a dormir ahora.",
                    "Me gusta el carro.",
                ]
                fib_prompt = 'Complete the phrase: "El plato del _____ (day)"'
                fib_answer = "día"
                fib_hint = "Spanish word for 'day'"
                wo_prompt = "Arrange the sentence: 'The food is very delicious.'"
                wo_order = ["La", "comida", "está", "muy", "deliciosa"]
                wo_distractors = ["ayer"]
                pairs = [
                    {"left": "Bread", "right": "El pan"},
                    {"left": "Delicious", "right": "Delicioso"},
                    {"left": "Table", "right": "La mesa"},
                    {"left": "Glass", "right": "El vaso"},
                ]
            elif "travel" in t or "direction" in t:
                mcq_prompt = "How do you ask 'Where is the train station?' in Spanish?"
                mcq_options = [
                    "¿Dónde está la estación de tren?",
                    "¿Cuándo comemos hoy?",
                    "¿Cómo te llamas?",
                ]
                fib_prompt = 'Complete the phrase: "Gire a la _____ (right)"'
                fib_answer = "derecha"
                fib_hint = "Spanish word for 'right'"
                wo_prompt = "Arrange the sentence: 'A ticket to Madrid, please.'"
                wo_order = ["Un", "billete", "para", "Madrid", "por", "favor"]
                wo_distractors = ["el", "tren"]
                pairs = [
                    {"left": "Airport", "right": "El aeropuerto"},
                    {"left": "Train", "right": "El tren"},
                    {"left": "Ticket", "right": "El billete"},
                    {"left": "Hotel", "right": "El hotel"},
                ]
            else:
                mcq_prompt = "How do you say 'Good morning, how are you?' in Spanish?"
                mcq_options = [
                    "Buenos días, ¿cómo estás?",
                    "Buenas noches, adiós.",
                    "Hasta luego, gracias.",
                ]
                fib_prompt = 'Complete the phrase: "Mucho _____ (nice to meet you)"'
                fib_answer = "gusto"
                fib_hint = "Spanish expression for 'pleasure'"
                wo_prompt = "Arrange the sentence: 'I speak a little Spanish.'"
                wo_order = ["Hablo", "un", "poco", "de", "español"]
                wo_distractors = ["mucho"]
                pairs = [
                    {"left": "Friend", "right": "El amigo"},
                    {"left": "House", "right": "La casa"},
                    {"left": "Today", "right": "Hoy"},
                    {"left": "Thank you", "right": "Gracias"},
                ]

        # --- FRENCH ---
        elif lang == "French":
            if "coffee" in t or "cafe" in t:
                mcq_prompt = "How do you order a coffee in French?"
                mcq_options = [
                    "Un café, s'il vous plaît.",
                    "Une bière, merci.",
                    "Une pomme, s'il vous plaît.",
                ]
                fib_prompt = (
                    'Complete the phrase: "Une table pour deux, s\'il vous _____"'
                )
                fib_answer = "plaît"
                fib_hint = "French for 'please'"
                wo_prompt = "Arrange the sentence: 'The check, please.'"
                wo_order = ["L'addition", "s'il", "vous", "plaît"]
                wo_distractors = ["le", "menu"]
                pairs = [
                    {"left": "Coffee", "right": "Le café"},
                    {"left": "Bill / Check", "right": "L'addition"},
                    {"left": "Water", "right": "L'eau"},
                    {"left": "Menu", "right": "Le menu"},
                ]
            elif "food" in t or "din" in t or "restaurant" in t:
                mcq_prompt = "How do you say 'I would like to order' in French?"
                mcq_options = [
                    "Je voudrais commander.",
                    "Je vais dormir.",
                    "J'aime la voiture.",
                ]
                fib_prompt = 'Complete the phrase: "Le plat du _____ (day)"'
                fib_answer = "jour"
                fib_hint = "French word for 'day'"
                wo_prompt = "Arrange the sentence: 'The food is very delicious.'"
                wo_order = ["La", "nourriture", "est", "très", "délicieuse"]
                wo_distractors = ["hier"]
                pairs = [
                    {"left": "Bread", "right": "Le pain"},
                    {"left": "Delicious", "right": "Délicieux"},
                    {"left": "Table", "right": "La table"},
                    {"left": "Glass", "right": "Le verre"},
                ]
            elif "travel" in t or "direction" in t:
                mcq_prompt = "How do you ask 'Where is the train station?' in French?"
                mcq_options = [
                    "Où est la gare?",
                    "Quand mangeons-nous?",
                    "Comment vous appelez-vous?",
                ]
                fib_prompt = 'Complete the phrase: "Tournez à _____ (right)"'
                fib_answer = "droite"
                fib_hint = "French word for 'right'"
                wo_prompt = "Arrange the sentence: 'A ticket to Paris, please.'"
                wo_order = ["Un", "billet", "pour", "Paris", "s'il", "vous", "plaît"]
                wo_distractors = ["le", "train"]
                pairs = [
                    {"left": "Airport", "right": "L'aéroport"},
                    {"left": "Train", "right": "Le train"},
                    {"left": "Ticket", "right": "Le billet"},
                    {"left": "Hotel", "right": "L'hôtel"},
                ]
            else:
                mcq_prompt = "How do you say 'Good morning, how are you?' in French?"
                mcq_options = [
                    "Bonjour, comment allez-vous?",
                    "Bonne nuit, au revoir.",
                    "À bientôt, merci.",
                ]
                fib_prompt = 'Complete the phrase: "Enchanté de faire votre _____ (acquaintance)"'
                fib_answer = "connaissance"
                fib_hint = "Formal French greeting"
                wo_prompt = "Arrange the sentence: 'I speak a little French.'"
                wo_order = ["Je", "parle", "un", "peu", "français"]
                wo_distractors = ["beaucoup"]
                pairs = [
                    {"left": "Friend", "right": "L'ami"},
                    {"left": "House", "right": "La maison"},
                    {"left": "Today", "right": "Aujourd'hui"},
                    {"left": "Thank you", "right": "Merci"},
                ]

        # --- GERMAN ---
        elif lang == "German":
            mcq_prompt = "How do you say 'Good morning' in German?"
            mcq_options = ["Guten Morgen", "Gute Nacht", "Auf Wiedersehen"]
            fib_prompt = 'Complete the phrase: "Eine Tasse Kaffee, _____ (please)"'
            fib_answer = "bitte"
            fib_hint = "German for 'please'"
            wo_prompt = "Arrange the sentence: 'I speak German.'"
            wo_order = ["Ich", "spreche", "Deutsch"]
            wo_distractors = ["Englisch"]
            pairs = [
                {"left": "Coffee", "right": "Der Kaffee"},
                {"left": "Water", "right": "Das Wasser"},
                {"left": "Thank you", "right": "Danke"},
                {"left": "Please", "right": "Bitte"},
            ]

        # --- ITALIAN ---
        elif lang == "Italian":
            mcq_prompt = "How do you say 'Good morning' in Italian?"
            mcq_options = ["Buongiorno", "Buonanotte", "Arrivederci"]
            fib_prompt = 'Complete the phrase: "Un caffè, per _____ (please)"'
            fib_answer = "favore"
            fib_hint = "Italian for 'please'"
            wo_prompt = "Arrange the sentence: 'I speak Italian.'"
            wo_order = ["Io", "parlo", "italiano"]
            wo_distractors = ["inglese"]
            pairs = [
                {"left": "Coffee", "right": "Il caffè"},
                {"left": "Water", "right": "L'acqua"},
                {"left": "Thank you", "right": "Grazie"},
                {"left": "Please", "right": "Per favore"},
            ]

        # --- GENERAL FALLBACK FOR OTHER LANGUAGES ---
        else:
            mcq_prompt = f"How do you say 'Hello' in {lang}?"
            mcq_options = [f"Hello ({lang})", f"Goodbye ({lang})", f"Thanks ({lang})"]
            fib_prompt = f'Complete the greeting in {lang}: "_____ (Hello)"'
            fib_answer = "Hello"
            fib_hint = f"Common greeting in {lang}"
            wo_prompt = f"Arrange the sentence in {lang}: 'I learn {lang}.'"
            wo_order = ["I", "learn", lang]
            wo_distractors = ["read"]
            pairs = [
                {"left": "Hello", "right": f"Hello ({lang})"},
                {"left": "Water", "right": f"Water ({lang})"},
                {"left": "Thank you", "right": f"Thank you ({lang})"},
                {"left": "Friend", "right": f"Friend ({lang})"},
            ]

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
    ) -> list[dict[str, Any]]:
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

            exercises.append(
                {
                    "quiz_id": quiz_id,
                    "type": "multiple_choice",
                    "position": pos,
                    "prompt": mcq.prompt,
                    "payload": {
                        "options": opts,
                        "correct_answer": mcq.correct_answer,
                    },
                }
            )
            pos += 1

        # 2. Fill in Blank
        for fib in content.fill_in_blank_exercises:
            if pos > count:
                break
            exercises.append(
                {
                    "quiz_id": quiz_id,
                    "type": "fill_in_blank",
                    "position": pos,
                    "prompt": fib.prompt,
                    "payload": {
                        "correct_answer": fib.correct_answer,
                        "hint": fib.hint,
                    },
                }
            )
            pos += 1

        # 3. Word Order
        for wo in content.word_order_exercises:
            if pos > count:
                break
            tokens = list(wo.correct_order)
            if wo.distractors:
                tokens.extend(wo.distractors)
            random.shuffle(tokens)

            exercises.append(
                {
                    "quiz_id": quiz_id,
                    "type": "word_order",
                    "position": pos,
                    "prompt": wo.prompt,
                    "payload": {
                        "tokens": tokens,
                        "correct_order": wo.correct_order,
                    },
                }
            )
            pos += 1

        # 4. Matching
        for match in content.matching_exercises:
            if pos > count:
                break
            exercises.append(
                {
                    "quiz_id": quiz_id,
                    "type": "matching",
                    "position": pos,
                    "prompt": match.prompt,
                    "payload": {
                        "pairs": [p.model_dump() for p in match.pairs],
                    },
                }
            )
            pos += 1

        return exercises

    async def execute_job(
        self, job_id: str, language: str, level: str, topic: str, count: int = 4
    ) -> str | None:
        """Executes full quiz generation lifecycle and records result in database."""
        try:
            # 1. Update job to in_progress
            now_iso = datetime.now(UTC).isoformat()
            self.db.table("generation_jobs").update(
                {
                    "status": "in_progress",
                    "started_at": now_iso,
                }
            ).eq("id", job_id).execute()

            # 2. Generate content (try Google GenAI SDK with Gemma 4 first)
            content = None
            if self.is_ai_available():
                logger.info(
                    f"Generating quiz with Google GenAI SDK ({settings.GEMINI_MODEL}) for topic='{topic}', lang='{language}'..."
                )
                content = await self.generate_with_gemini(language, level, topic, count)

            if not content:
                logger.info(
                    f"Using dynamic curriculum engine for quiz generation in {language}..."
                )
                content = self.generate_fallback_content(language, level, topic, count)

            # 3. Insert Quiz record
            quiz_insert = (
                self.db.table("quizzes")
                .insert(
                    {
                        "title": content.title or f"{topic} in {language}",
                        "topic": topic,
                        "language": language,
                        "level": level,
                    }
                )
                .execute()
            )

            if not quiz_insert.data:
                raise Exception("Failed to insert generated quiz into database")

            quiz_id = str(quiz_insert.data[0]["id"])

            # 4. Insert Exercises
            exercise_records = self._convert_to_exercise_records(
                content, quiz_id, count
            )
            for ex in exercise_records:
                self.db.table("exercises").insert(ex).execute()

            # 5. Mark job completed
            completed_iso = datetime.now(UTC).isoformat()
            self.db.table("generation_jobs").update(
                {
                    "status": "completed",
                    "quiz_id": quiz_id,
                    "completed_at": completed_iso,
                }
            ).eq("id", job_id).execute()

            logger.info(f"Quiz generation job {job_id} succeeded with quiz {quiz_id}")
            return quiz_id

        except Exception as exc:
            logger.exception(f"Quiz generation job {job_id} failed: {exc}")
            self.db.table("generation_jobs").update(
                {
                    "status": "failed",
                    "error": str(exc),
                    "completed_at": datetime.now(UTC).isoformat(),
                }
            ).eq("id", job_id).execute()
            return None
