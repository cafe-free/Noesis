from pydantic import BaseModel
from typing import List

class BasicStatisticsResponse(BaseModel):
    total_quizzes: int
    completed_quizzes: int
    total_exercises: int
    correct_answers: int
    accuracy: float

class Weakness(BaseModel):
    topic: str
    accuracy: float

class WeaknessesResponse(BaseModel):
    weaknesses: List[Weakness]
