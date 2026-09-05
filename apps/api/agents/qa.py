from apps.api.agents.base import LLMProvider
from apps.api.schemas.generation import QAValidationResult

class QAAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def _deterministic_validation(self, exercise: dict) -> QAValidationResult:
        # Schema and basic sanity checks
        issues = []
        payload = exercise.get("payload", {})
        
        if exercise["type"] == "mcq_translation":
            if len(set(payload.get("choices", []))) != len(payload.get("choices", [])):
                issues.append("Duplicate choices found.")
            if payload.get("correct_answer") not in payload.get("choices", []):
                issues.append("Correct answer is not in choices.")
                
        elif exercise["type"] == "fill_blank":
            if "____" not in payload.get("sentence", ""):
                issues.append("Sentence missing blank '____'.")
                
        if issues:
            return QAValidationResult(valid=False, issues=issues)
        
        return QAValidationResult(valid=True, issues=[])

    async def validate_exercise(self, language: str, level: str, exercise: dict) -> QAValidationResult:
        # 1. Deterministic validation
        det_result = self._deterministic_validation(exercise)
        if not det_result.valid:
            return det_result

        # 2. Linguistic validation via LLM
        prompt = f"""
        You are a Quality Assurance expert for {language} ({level} level) learning materials.
        Please review the following exercise and determine if it's perfectly valid, grammatically correct, and appropriate for the level.
        
        Exercise:
        {exercise}
        
        If it has issues (e.g., correct answer is wrong, distractors are actually valid answers, inappropriate difficulty), list them.
        If it's perfect, set valid=true.
        """
        
        return await self.provider.generate_structured(prompt, QAValidationResult)
