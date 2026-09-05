import pytest
from apps.api.main import app
from fastapi.testclient import TestClient
from apps.api.agents.base import LLMProvider
from pydantic import BaseModel
import asyncio
from typing import Type

@pytest.fixture
def client():
    return TestClient(app)

class MockLLMProvider(LLMProvider):
    async def generate_structured(self, prompt: str, response_model: Type[BaseModel]) -> BaseModel:
        # We need a way to mock responses based on the response_model
        if response_model.__name__ == "CurriculumSchema":
            return response_model(
                language="Spanish",
                level="A1",
                topic="Food",
                learning_objectives=["Learn basic food vocabulary", "Practice first-person present tense"],
                vocabulary=["apple", "banana", "eat", "drink"],
                grammar=["Present tense"]
            )
        elif response_model.__name__ == "GeneratedExercisesResponse":
            from apps.api.agents.exercise import RawExerciseData
            return response_model(
                exercises=[
                    RawExerciseData(
                        type="mcq_translation",
                        prompt="I eat apples.",
                        payload={
                            "source_text": "I eat apples.",
                            "correct_answer": "Yo como manzanas."
                        }
                    )
                ]
            )
        elif response_model.__name__ == "DistractorResponse":
            return response_model(distractors=["Yo come manzanas.", "Yo comen manzanas.", "Yo comí manzanas."])
        elif response_model.__name__ == "QAValidationResult":
            return response_model(valid=True, issues=[])
            
        raise ValueError(f"No mock defined for {response_model.__name__}")

@pytest.fixture
def mock_provider():
    return MockLLMProvider()
