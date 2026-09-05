from apps.api.agents.base import LLMProvider
from apps.api.schemas.generation import CurriculumSchema

class CurriculumAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def generate_curriculum(self, language: str, level: str, topic: str) -> CurriculumSchema:
        prompt = f"""
        You are an expert curriculum designer for language learning.
        Design a micro-curriculum for learning {language} at the {level} CEFR level.
        The topic is: {topic}.
        
        Provide:
        - 2-3 specific learning objectives.
        - A list of key vocabulary words (4-10 words).
        - Key grammatical concepts being practiced (1-3 concepts).
        """
        
        return await self.provider.generate_structured(prompt, CurriculumSchema)
