import redis.asyncio as redis
from apps.api.core.config import get_settings

settings = get_settings()

async def get_redis():
    return redis.from_url(settings.REDIS_URL, decode_responses=True)
