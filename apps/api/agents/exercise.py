from typing import List, Any
from pydantic import BaseModel
from apps.api.agents.base import LLMProvider
from apps.api.schemas.generation import CurriculumSchema
import random
import json

class RawExerciseData(BaseModel):
    type: str
    prompt: str
    payload: dict

class GeneratedExercisesResponse(BaseModel):
    exercises: List[RawExerciseData]

class ExerciseAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def generate_exercises(self, language: str, level: str, topic: str, curriculum: CurriculumSchema, count: int) -> List[dict]:
        prompt = f"""
        You are an expert language teacher creating exercises for {language} learners at {level} level.
        The topic is: {topic}.
        
        Curriculum constraints:
        Objectives: {', '.join(curriculum.learning_objectives)}
        Vocabulary: {', '.join(curriculum.vocabulary)}
        Grammar: {', '.join(curriculum.grammar)}
        
        Generate exactly {count} exercises.
        Distribute them roughly as: 40% mcq_translation, 30% fill_blank, 20% word_order, 10% matching.
        
        For "mcq_translation", the payload must have: "source_text", "correct_answer", and we will generate "choices" later, so leave "choices" empty array for now.
        For "fill_blank", the payload must have: "sentence" (with '____'), "correct_answer", "acceptable_answers" (list).
        For "word_order", the payload must have: "correct_order" (list of words), and we will shuffle them for "tokens" later, so you can leave "tokens" empty or provide a shuffled list.
        For "matching", the payload must have: "pairs" (list of objects with "left" and "right").
        
        Return the result as a list of exercises matching the requested format.
        """
        
        response = await self.provider.generate_structured(prompt, GeneratedExercisesResponse)
        
        # Post-process if needed
        exercises = []
        for raw in response.exercises:
            ex = {
                "type": raw.type,
                "prompt": raw.prompt,
                "payload": raw.payload
            }
            exercises.append(ex)
            
        return exercises
