from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class ProgressResponse(BaseModel):
    id: UUID
    name: str
    email: str
    avatar: Optional[str] = None
    learningLanguage: str = "Spanish"
    nativeLanguage: str = "English"
    currentLevel: str = "A1"
    streakDays: int = 1
    totalXp: int = 0
    dailyGoalXp: int = 50
    todayXp: int = 0
    hearts: int = 5
    maxHearts: int = 5


class WeakAreaItemResponse(BaseModel):
    id: str
    topic: str
    concept: str
    accuracyRate: int
    mistakeCount: int
    lastPracticed: str
