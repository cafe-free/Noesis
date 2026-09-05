from apps.api.agents.base import LLMProvider
from pydantic import BaseModel
from typing import List

class DistractorResponse(BaseModel):
    distractors: List[str]

class DistractorAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def generate_distractors(self, language: str, level: str, exercise_type: str, payload: dict) -> dict:
        if exercise_type != "mcq_translation":
            return payload

        correct_answer = payload.get("correct_answer")
        source_text = payload.get("source_text")
        
        if not correct_answer or not source_text:
            return payload

        prompt = f"""
        Generate exactly 3 plausible but incorrect options (distractors) for a multiple-choice translation exercise.
        Language: {language}
        Level: {level}
        
        Original text: "{source_text}"
        Correct translation: "{correct_answer}"
        
        The distractors should reflect realistic learner mistakes (e.g., wrong verb conjugation, wrong gender, false friends).
        They MUST NOT be grammatically correct translations of the original text.
        """
        
        response = await self.provider.generate_structured(prompt, DistractorResponse)
        
        choices = [correct_answer] + response.distractors
        # In a real app we'd shuffle, but we can just store them and shuffle on the frontend,
        # or shuffle here. Let's shuffle here.
        import random
        random.shuffle(choices)
        
        payload["choices"] = choices
        return payload
