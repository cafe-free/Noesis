from fastapi import APIRouter
from apps.api.schemas.attempt import AnswerSubmissionRequest, AnswerSubmissionResponse
from apps.api.services.quiz import QuizService

router = APIRouter(prefix="/attempts", tags=["attempts"])

@router.post("", response_model=AnswerSubmissionResponse)
async def submit_attempt(request: AnswerSubmissionRequest):
    service = QuizService()
    return service.evaluate_attempt(request)
