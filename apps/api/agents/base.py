from abc import ABC, abstractmethod
from pydantic import BaseModel
import json
from google import genai
from google.genai import types
from apps.api.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class LLMProvider(ABC):
    @abstractmethod
    async def generate_structured(self, prompt: str, response_model: type[BaseModel]) -> BaseModel:
        pass

class GeminiProvider(LLMProvider):
    def __init__(self):
        # We assume GEMINI_API_KEY is available in settings
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-2.5-flash"

    async def generate_structured(self, prompt: str, response_model: type[BaseModel]) -> BaseModel:
        retries = settings.MAX_LLM_RETRIES
        for attempt in range(retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=response_model,
                    ),
                )
                
                # Try to parse the JSON response
                try:
                    data = json.loads(response.text)
                    return response_model.model_validate(data)
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse or validate JSON on attempt {attempt + 1}: {e}")
                    if attempt == retries:
                        raise ValueError(f"Failed to generate structured response after {retries + 1} attempts") from e
            except Exception as e:
                logger.warning(f"API call failed on attempt {attempt + 1}: {e}")
                if attempt == retries:
                    raise e
